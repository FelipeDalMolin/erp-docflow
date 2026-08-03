"""Manifest, controls, path confinement and input integrity contracts."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from conftest import SyntheticRepository

from erp_docflow_experiment.candidates import run_integrity_probe
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.manifest import prepare_experiment
from erp_docflow_experiment.models import parse_manifest
from erp_docflow_experiment.repository import (
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
    assert _reason(caught) == "SCHEMA_INVALID"


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
