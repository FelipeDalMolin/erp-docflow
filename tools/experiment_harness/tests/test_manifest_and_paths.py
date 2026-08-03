"""Manifest, controls, path confinement and input integrity contracts."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

import pytest
from conftest import SyntheticRepository

import erp_docflow_experiment.manifest as manifest_module
from erp_docflow_experiment.candidates import run_integrity_probe
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.manifest import prepare_experiment
from erp_docflow_experiment.models import parse_manifest
from erp_docflow_experiment.repository import (
    create_staging_directory,
    publish_staging_directory,
    resolve_existing_bundle,
    resolve_output_directory,
    resolve_repo_file,
)
from erp_docflow_experiment.runner import validate_experiment


def _reason(error: pytest.ExceptionInfo[HarnessError]) -> str:
    return error.value.reason_code


def test_valid_manifest_resolves_every_static_input(
    synthetic_repo: SyntheticRepository,
) -> None:
    result = validate_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert result == {
        "status": "VALID",
        "schema_version": "experiment-manifest/v1alpha",
        "experiment_id": "pytest-integrity-probe",
        "candidate": "integrity_probe/v1",
        "selected_fixture_count": 1,
        "dataset_classification": "synthetic",
    }


def test_input_digest_is_derived_from_the_exact_bytes_that_were_parsed(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_bytes = synthetic_repo.dataset_path.read_bytes()
    original_loader = manifest_module.load_json_object_with_bytes
    mutated = False

    def load_then_mutate(
        path: Path,
        context: str,
        *,
        confinement_root: Path | None = None,
    ) -> tuple[dict[str, object], bytes]:
        nonlocal mutated
        value, raw = original_loader(
            path,
            context,
            confinement_root=confinement_root,
        )
        if path == synthetic_repo.dataset_path and not mutated:
            changed = synthetic_repo.dataset_copy()
            changed["concurrent_change"] = True
            synthetic_repo.write_dataset(changed)
            mutated = True
        return value, raw

    monkeypatch.setattr(
        manifest_module,
        "load_json_object_with_bytes",
        load_then_mutate,
    )

    prepared = prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert prepared.input_digests["dataset_manifest"] == hashlib.sha256(
        original_bytes
    ).hexdigest()
    assert prepared.input_digests["dataset_manifest"] != hashlib.sha256(
        synthetic_repo.dataset_path.read_bytes()
    ).hexdigest()


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        (lambda value: value.pop("purpose"), "SCHEMA_INVALID"),
        (lambda value: value.update({"unknown": True}), "SCHEMA_INVALID"),
        (
            lambda value: value.update({"schema_version": "experiment-manifest/v2"}),
            "SCHEMA_VERSION_UNSUPPORTED",
        ),
        (lambda value: value.update({"issue": True}), "SCHEMA_INVALID"),
        (lambda value: value.update({"dataset_classification": "real"}), "REAL_DATA_NOT_ALLOWED"),
    ],
)
def test_invalid_manifest_fails_closed(
    synthetic_repo: SyntheticRepository,
    mutation: object,
    expected_reason: str,
) -> None:
    value = synthetic_repo.manifest_copy()
    assert callable(mutation)
    mutation(value)

    with pytest.raises(HarnessError) as caught:
        parse_manifest(value)

    assert _reason(caught) == expected_reason


def test_malformed_json_has_typed_failure(synthetic_repo: SyntheticRepository) -> None:
    synthetic_repo.manifest_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == "JSON_INVALID"


def test_unknown_candidate_cannot_escape_closed_registry(
    synthetic_repo: SyntheticRepository,
) -> None:
    value = synthetic_repo.manifest_copy()
    candidate = value["candidate"]
    assert isinstance(candidate, dict)
    candidate["id"] = "shell://arbitrary-command"
    synthetic_repo.write_manifest(value)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == "CANDIDATE_NOT_REGISTERED"


@pytest.mark.parametrize(
    ("field", "value", "expected_reason"),
    [
        ("runtime_egress_allowed", True, "EGRESS_NOT_ALLOWED"),
        ("real_data_allowed", True, "REAL_DATA_NOT_ALLOWED"),
        ("max_parallel_jobs", 2, "CONCURRENCY_NOT_ALLOWED"),
        ("timeout_seconds", 0, "SCHEMA_INVALID"),
        ("timeout_seconds", 86401, "SCHEMA_INVALID"),
        ("random_seed", -1, "SCHEMA_INVALID"),
        ("random_seed", 4294967296, "SCHEMA_INVALID"),
    ],
)
def test_execution_controls_are_fail_closed(
    synthetic_repo: SyntheticRepository,
    field: str,
    value: object,
    expected_reason: str,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    controls = manifest["controls"]
    assert isinstance(controls, dict)
    controls[field] = value
    synthetic_repo.write_manifest(manifest)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == expected_reason


def test_candidate_configuration_and_capability_are_owned_by_registry(
    synthetic_repo: SyntheticRepository,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    manifest["capability"] = "probe_document"
    synthetic_repo.write_manifest(manifest)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)
    assert _reason(caught) == "CAPABILITY_MISMATCH"

    manifest = synthetic_repo.manifest_copy()
    candidate = manifest["candidate"]
    assert isinstance(candidate, dict)
    candidate["configuration"] = {"verify_ground_truth": False}
    synthetic_repo.write_manifest(manifest)
    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)
    assert _reason(caught) == "CANDIDATE_CONFIGURATION_INVALID"


def test_candidate_must_use_the_dependency_lock_that_governs_execution(
    synthetic_repo: SyntheticRepository,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    manifest["dependency_lock_ref"] = ".gitignore"
    synthetic_repo.write_manifest(manifest)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == "DEPENDENCY_LOCK_MISMATCH"


def test_missing_and_traversing_input_references_are_rejected(
    synthetic_repo: SyntheticRepository,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    manifest["profile_ref"] = "profiles/missing.json"
    synthetic_repo.write_manifest(manifest)
    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)
    assert _reason(caught) == "INPUT_NOT_FOUND"

    manifest["profile_ref"] = "../outside.json"
    synthetic_repo.write_manifest(manifest)
    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)
    assert _reason(caught) == "PATH_NOT_ALLOWED"


def test_manifest_itself_must_be_inside_repository(
    synthetic_repo: SyntheticRepository,
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, outside)

    assert _reason(caught) == "PATH_NOT_ALLOWED"


def test_dataset_member_traversal_is_rejected_at_execution(
    synthetic_repo: SyntheticRepository,
) -> None:
    dataset = synthetic_repo.dataset_copy()
    fixtures = dataset["fixtures"]
    assert isinstance(fixtures, list)
    fixture = fixtures[0]
    assert isinstance(fixture, dict)
    fixture["path"] = "../outside.pdf"
    synthetic_repo.write_dataset(dataset)
    prepared = prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    with pytest.raises(HarnessError) as caught:
        run_integrity_probe(synthetic_repo.root, prepared, time.monotonic() + 10)

    assert _reason(caught) == "PATH_NOT_ALLOWED"


@pytest.mark.parametrize("field", ["sha256", "size_bytes"])
def test_fixture_digest_or_size_divergence_fails(
    synthetic_repo: SyntheticRepository,
    field: str,
) -> None:
    dataset = synthetic_repo.dataset_copy()
    fixtures = dataset["fixtures"]
    assert isinstance(fixtures, list)
    fixture = fixtures[0]
    assert isinstance(fixture, dict)
    fixture[field] = "0" * 64 if field == "sha256" else 999999
    synthetic_repo.write_dataset(dataset)
    prepared = prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    with pytest.raises(HarnessError) as caught:
        run_integrity_probe(synthetic_repo.root, prepared, time.monotonic() + 10)

    assert _reason(caught) == "INTEGRITY_MISMATCH"


@pytest.mark.parametrize("field", ["ground_truth_sha256", "ground_truth_size_bytes"])
def test_ground_truth_digest_or_size_divergence_fails(
    synthetic_repo: SyntheticRepository,
    field: str,
) -> None:
    dataset = synthetic_repo.dataset_copy()
    fixtures = dataset["fixtures"]
    assert isinstance(fixtures, list)
    fixture = fixtures[0]
    assert isinstance(fixture, dict)
    fixture[field] = "0" * 64 if field.endswith("sha256") else 999999
    synthetic_repo.write_dataset(dataset)
    prepared = prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    with pytest.raises(HarnessError) as caught:
        run_integrity_probe(synthetic_repo.root, prepared, time.monotonic() + 10)

    assert _reason(caught) == "INTEGRITY_MISMATCH"


def test_timeout_is_typed_and_does_not_return_empty_success(
    synthetic_repo: SyntheticRepository,
) -> None:
    prepared = prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    with pytest.raises(HarnessError) as caught:
        run_integrity_probe(synthetic_repo.root, prepared, time.monotonic() - 1)

    assert _reason(caught) == "TIMEOUT_EXCEEDED"


def test_fixture_selection_is_sorted_and_counted(
    synthetic_repo: SyntheticRepository,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    selector = manifest["fixture_selector"]
    assert isinstance(selector, dict)
    selector["expected_fixture_count"] = 2
    synthetic_repo.write_manifest(manifest)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == "FIXTURE_COUNT_MISMATCH"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("experiment_id", "INVALID ID"),
        ("purpose", "x" * 1001),
        ("capability", "x" * 129),
    ],
)
def test_manifest_string_contract_limits_are_enforced(
    synthetic_repo: SyntheticRepository,
    field: str,
    invalid_value: str,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    manifest[field] = invalid_value

    with pytest.raises(HarnessError) as caught:
        parse_manifest(manifest)

    assert _reason(caught) == "SCHEMA_INVALID"


def test_fixture_selector_split_and_id_contracts_are_enforced(
    synthetic_repo: SyntheticRepository,
) -> None:
    manifest = synthetic_repo.manifest_copy()
    selector = manifest["fixture_selector"]
    assert isinstance(selector, dict)
    selector["splits"] = ["unknown"]

    with pytest.raises(HarnessError) as caught:
        parse_manifest(manifest)
    assert _reason(caught) == "SCHEMA_INVALID"

    selector["splits"] = ["test"]
    selector["fixture_ids"] = ["INVALID_ID"]
    with pytest.raises(HarnessError) as caught:
        parse_manifest(manifest)
    assert _reason(caught) == "SCHEMA_INVALID"


def test_hash_deadline_is_checked_during_incremental_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from erp_docflow_experiment.jsonio import sha256_file

    source = tmp_path / "source.bin"
    source.write_bytes(b"synthetic bytes")
    moments = iter((0.0, 2.0))
    monkeypatch.setattr(
        "erp_docflow_experiment.jsonio.time.monotonic",
        lambda: next(moments),
    )

    with pytest.raises(HarnessError) as caught:
        sha256_file(source, deadline=1.0)

    assert _reason(caught) == "TIMEOUT_EXCEEDED"


def test_output_is_confined_and_never_overwritten(
    synthetic_repo: SyntheticRepository,
    tmp_path: Path,
) -> None:
    allowed = resolve_output_directory(
        synthetic_repo.root,
        Path(".artifacts/experiments/new-bundle"),
    )
    assert allowed == synthetic_repo.root / ".artifacts" / "experiments" / "new-bundle"

    for disallowed in (
        Path(".artifacts/experiments"),
        Path(".artifacts/experiments/unsafe;command"),
        Path("../escape"),
        tmp_path / "absolute-escape",
    ):
        with pytest.raises(HarnessError) as caught:
            resolve_output_directory(synthetic_repo.root, disallowed)
        assert _reason(caught) == "OUTPUT_PATH_NOT_ALLOWED"

    allowed.mkdir(parents=True)
    with pytest.raises(HarnessError) as caught:
        resolve_output_directory(synthetic_repo.root, Path(".artifacts/experiments/new-bundle"))
    assert _reason(caught) == "OUTPUT_ALREADY_EXISTS"


def test_symlink_inserted_after_resolution_cannot_redirect_staging(
    synthetic_repo: SyntheticRepository,
    tmp_path: Path,
) -> None:
    requested = Path(".artifacts/experiments/nested/new-bundle")
    output = resolve_output_directory(synthetic_repo.root, requested)
    outside = tmp_path / "outside-output"
    outside.mkdir()
    nested = synthetic_repo.root / ".artifacts" / "experiments" / "nested"
    nested.parent.mkdir(parents=True)
    nested.symlink_to(outside, target_is_directory=True)

    with pytest.raises(HarnessError) as caught:
        create_staging_directory(synthetic_repo.root, output)

    assert _reason(caught) == "OUTPUT_CREATE_FAILED"
    assert list(outside.iterdir()) == []


def test_atomic_publication_never_replaces_a_racing_destination(
    synthetic_repo: SyntheticRepository,
) -> None:
    output = resolve_output_directory(
        synthetic_repo.root,
        Path(".artifacts/experiments/racing-output"),
    )
    staging, identity = create_staging_directory(synthetic_repo.root, output)
    output.mkdir()
    marker = output / "preexisting-marker.txt"
    marker.write_text("preserve me", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        publish_staging_directory(staging, identity, output)

    assert _reason(caught) == "OUTPUT_ALREADY_EXISTS"
    assert marker.read_text(encoding="utf-8") == "preserve me"
    assert staging.is_dir()


def test_repository_reference_rejects_noncanonical_path(
    synthetic_repo: SyntheticRepository,
) -> None:
    with pytest.raises(HarnessError) as caught:
        resolve_repo_file(
            synthetic_repo.root,
            "profiles//synthetic/v1alpha/profile.json",
            "profile_ref",
        )

    assert _reason(caught) == "PATH_NOT_ALLOWED"


def test_evidence_root_symlinks_are_rejected(
    synthetic_repo: SyntheticRepository,
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside-artifacts"
    (outside / "experiments" / "bundle").mkdir(parents=True)
    (synthetic_repo.root / ".artifacts").symlink_to(outside, target_is_directory=True)

    with pytest.raises(HarnessError) as caught:
        resolve_output_directory(
            synthetic_repo.root,
            Path(".artifacts/experiments/new-bundle"),
        )
    assert _reason(caught) == "OUTPUT_PATH_NOT_ALLOWED"

    with pytest.raises(HarnessError) as caught:
        resolve_existing_bundle(
            synthetic_repo.root,
            Path(".artifacts/experiments/bundle"),
        )
    assert _reason(caught) == "BUNDLE_NOT_FOUND"


def test_cross_references_must_resolve_to_the_same_experiment_inputs(
    synthetic_repo: SyntheticRepository,
) -> None:
    dataset = synthetic_repo.dataset_copy()
    dataset["profile_ref"] = "profiles/another/v1alpha/profile.json"
    synthetic_repo.write_dataset(dataset)

    with pytest.raises(HarnessError) as caught:
        prepare_experiment(synthetic_repo.root, synthetic_repo.manifest_path)

    assert _reason(caught) == "INPUT_REFERENCE_MISMATCH"
