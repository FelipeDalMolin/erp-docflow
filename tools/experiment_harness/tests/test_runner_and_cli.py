"""End-to-end runner, failure evidence, CLI and redaction tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from conftest import SyntheticRepository

from erp_docflow_experiment.bundle import verify_bundle
from erp_docflow_experiment.cli import main
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import canonical_json_bytes
from erp_docflow_experiment.repository import find_repo_root
from erp_docflow_experiment.runner import _git, _host_class, run_experiment

REPO_ROOT = find_repo_root(Path(__file__))


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_host_class_is_derived_from_the_observed_resource_envelope() -> None:
    assert _host_class(3, 5 * 1024**3) == (
        "observed-cpu-3-memory-5gib-gpu-not-declared"
    )
    assert _host_class(None, None) == (
        "observed-cpu-unknown-memory-unknown-gpu-not-declared"
    )


def test_successful_run_materializes_verifiable_factual_evidence(
    synthetic_repo: SyntheticRepository,
) -> None:
    result = run_experiment(
        synthetic_repo.root,
        synthetic_repo.manifest_path,
        Path(".artifacts/experiments/success"),
    )
    output = synthetic_repo.root / ".artifacts" / "experiments" / "success"

    assert result["status"] == "SUCCEEDED"
    assert result["selected_fixture_count"] == 1
    assert verify_bundle(output)["artifact_count"] == 4

    record = _load(output / "benchmark-run.json")
    assert record["status"] == "SUCCEEDED"
    assert record["selected_fixture_count"] == 1
    assert record["succeeded_fixture_count"] == 1
    assert record["failure"] is None
    assert "promotion_decision_ref" not in record
    assert not (output / "promotion-decision.json").exists()

    provenance = record["provenance"]
    assert isinstance(provenance, dict)
    assert len(str(provenance["git_commit"])) == 40
    assert provenance["workspace_clean"] is True
    assert set(provenance["input_sha256"]) == {
        "acceptance_policy",
        "candidate_configuration",
        "dataset_manifest",
        "dependency_lock",
        "experiment_manifest",
        "profile",
    }
    input_sha256 = provenance["input_sha256"]
    assert isinstance(input_sha256, dict)
    assert input_sha256["candidate_configuration"] == hashlib.sha256(
        canonical_json_bytes({"verify_ground_truth": True})
    ).hexdigest()
    environment = record["environment"]
    assert isinstance(environment, dict)
    assert str(environment["host_class"]).startswith("observed-cpu-")
    assert environment["host_class"] != "small-cpu-lab"
    assert environment["cpu"] != "unknown"
    assert "memory_total_bytes" in environment
    assert "memory_available_bytes" in environment


def test_emitted_run_matches_every_closed_required_schema_shape(
    synthetic_repo: SyntheticRepository,
) -> None:
    requested = Path(".artifacts/experiments/schema-shape")
    run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)
    record = _load(synthetic_repo.root / requested / "benchmark-run.json")
    schema = _load(REPO_ROOT / "experiments/schemas/v1alpha/benchmark-run.schema.json")

    required = schema["required"]
    properties = schema["properties"]
    definitions = schema["$defs"]
    assert isinstance(required, list)
    assert isinstance(properties, dict)
    assert isinstance(definitions, dict)
    assert set(record) == set(required) == set(properties)

    for field, definition_name in (
        ("provenance", "provenance"),
        ("environment", "environment"),
        ("controls", "controls"),
        ("artifacts", "artifacts"),
    ):
        value = record[field]
        definition = definitions[definition_name]
        assert isinstance(value, dict)
        assert isinstance(definition, dict)
        child_required = definition["required"]
        child_properties = definition["properties"]
        assert isinstance(child_required, list)
        assert isinstance(child_properties, dict)
        assert set(value) == set(child_required) == set(child_properties)

    provenance = record["provenance"]
    assert isinstance(provenance, dict)
    input_sha256 = provenance["input_sha256"]
    provenance_schema = definitions["provenance"]
    assert isinstance(input_sha256, dict)
    assert isinstance(provenance_schema, dict)
    provenance_properties = provenance_schema["properties"]
    assert isinstance(provenance_properties, dict)
    input_schema = provenance_properties["input_sha256"]
    assert isinstance(input_schema, dict)
    input_required = input_schema["required"]
    input_properties = input_schema["properties"]
    assert isinstance(input_required, list)
    assert isinstance(input_properties, dict)
    assert set(input_sha256) == set(input_required) == set(input_properties)
    assert all(
        isinstance(digest, str)
        and len(digest) == 64
        and set(digest).issubset(set("0123456789abcdef"))
        for digest in input_sha256.values()
    )


def test_existing_output_is_not_overwritten(synthetic_repo: SyntheticRepository) -> None:
    requested = Path(".artifacts/experiments/existing")
    run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "OUTPUT_ALREADY_EXISTS"


def test_empty_candidate_result_is_materialized_as_failure_not_success(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def empty_candidate(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
        return []

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", empty_candidate)
    requested = Path(".artifacts/experiments/empty-result")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "CANDIDATE_RESULT_INVALID"
    output = synthetic_repo.root / requested
    record = _load(output / "benchmark-run.json")
    assert record["status"] == "FAILED"
    assert record["succeeded_fixture_count"] == 0
    assert _load(output / "fixture-results.json") == {"results": []}
    assert verify_bundle(output)["status"] == "VERIFIED"


def test_unsafe_candidate_result_is_discarded_without_leaking_content(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "candidate-secret-that-must-not-be-materialized"
    unsafe = {
        "fixture_id": "fixture-one",
        "status": "SUCCEEDED",
        "reason_code": "INTEGRITY_OK",
        "content": secret,
    }

    def unsafe_candidate(
        _repo_root: Path,
        _prepared: object,
        _deadline: float,
        on_result: object,
    ) -> list[dict[str, object]]:
        assert callable(on_result)
        on_result(unsafe)
        return [unsafe]

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", unsafe_candidate)
    requested = Path(".artifacts/experiments/unsafe-result")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "CANDIDATE_RESULT_INVALID"
    output = synthetic_repo.root / requested
    materialized = "".join(
        path.read_text(encoding="utf-8")
        for path in output.iterdir()
        if path.is_file()
    )
    assert secret not in materialized
    assert _load(output / "fixture-results.json") == {"results": []}


def test_candidate_failure_persists_failed_bundle_without_empty_success(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = HarnessError("INTEGRITY_MISMATCH", "synthetic integrity failure")

    def fail_candidate(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
        raise failure

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", fail_candidate)
    requested = Path(".artifacts/experiments/failed")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)
    assert caught.value.reason_code == "INTEGRITY_MISMATCH"

    output = synthetic_repo.root / requested
    record = _load(output / "benchmark-run.json")
    assert record["status"] == "FAILED"
    assert record["succeeded_fixture_count"] == 0
    assert record["failure"] == {
        "reason_code": "INTEGRITY_MISMATCH",
        "message": "synthetic integrity failure",
    }
    assert _load(output / "fixture-results.json") == {"results": []}
    assert verify_bundle(output)["status"] == "VERIFIED"
    events = (output / "events.jsonl").read_text(encoding="utf-8")
    assert '"event":"candidate_failed"' in events
    assert '"status":"FAILED"' in events
    assert '"status":"SUCCEEDED"' not in events


def test_real_integrity_failure_records_failed_fixture_and_reason(
    synthetic_repo: SyntheticRepository,
) -> None:
    synthetic_repo.fixture_path.write_bytes(b"tampered synthetic bytes")
    requested = Path(".artifacts/experiments/integrity-failure")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "INTEGRITY_MISMATCH"
    output = synthetic_repo.root / requested
    record = _load(output / "benchmark-run.json")
    assert record["status"] == "FAILED"
    assert record["succeeded_fixture_count"] == 0
    assert _load(output / "fixture-results.json") == {
        "results": [
            {
                "fixture_id": "fixture-one",
                "status": "FAILED",
                "reason_code": "INTEGRITY_MISMATCH",
            }
        ]
    }
    assert verify_bundle(output)["status"] == "VERIFIED"


def test_unexpected_candidate_failure_is_redacted_and_materialized(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "provider-secret-that-must-not-leak"

    def fail_candidate(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
        raise RuntimeError(secret)

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", fail_candidate)
    requested = Path(".artifacts/experiments/unexpected-failure")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "CANDIDATE_EXECUTION_FAILED"
    output = synthetic_repo.root / requested
    record_text = (output / "benchmark-run.json").read_text(encoding="utf-8")
    events_text = (output / "events.jsonl").read_text(encoding="utf-8")
    assert secret not in record_text + events_text
    assert _load(output / "benchmark-run.json")["failure"] == {
        "reason_code": "CANDIDATE_EXECUTION_FAILED",
        "message": "candidate execution failed",
    }
    assert verify_bundle(output)["status"] == "VERIFIED"


def test_operator_interrupt_is_typed_and_materialized_before_returning_nonzero(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def interrupt_candidate(*_args: object, **_kwargs: object) -> list[dict[str, object]]:
        raise KeyboardInterrupt

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", interrupt_candidate)
    monkeypatch.chdir(synthetic_repo.root)
    requested = ".artifacts/experiments/operator-interrupt"

    exit_code = main(
        [
            "run",
            "--manifest",
            "experiments/synthetic/v1alpha/smoke.json",
            "--output",
            requested,
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert json.loads(captured.err)["reason_code"] == "OPERATOR_INTERRUPTED"
    output = synthetic_repo.root / requested
    record = _load(output / "benchmark-run.json")
    assert record["status"] == "FAILED"
    assert record["failure"] == {
        "reason_code": "OPERATOR_INTERRUPTED",
        "message": "experiment interrupted by operator",
    }
    assert verify_bundle(output)["status"] == "VERIFIED"


def test_provenance_failure_does_not_create_an_empty_output(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_git(*_args: object, **_kwargs: object) -> str:
        raise HarnessError("PROVENANCE_UNAVAILABLE", "cannot capture Git provenance")

    monkeypatch.setattr("erp_docflow_experiment.runner._git", fail_git)
    requested = Path(".artifacts/experiments/no-provenance")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "PROVENANCE_UNAVAILABLE"
    assert not (synthetic_repo.root / requested).exists()


def test_artifact_finalization_failure_never_publishes_requested_output(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_bundle(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise HarnessError("ARTIFACT_WRITE_FAILED", "cannot write an evidence artifact")

    monkeypatch.setattr("erp_docflow_experiment.runner.create_bundle", fail_bundle)
    requested = Path(".artifacts/experiments/finalization-failed")

    with pytest.raises(HarnessError) as caught:
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    assert caught.value.reason_code == "ARTIFACT_WRITE_FAILED"
    assert not (synthetic_repo.root / requested).exists()
    staging = list(
        (synthetic_repo.root / ".artifacts" / "experiments").glob(
            ".erp-docflow-staging-*"
        )
    )
    assert len(staging) == 1
    assert not (staging[0] / "artifact-bundle.json").exists()


def test_partial_candidate_results_remain_factual_on_failure(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixtures = synthetic_repo.dataset["fixtures"]
    assert isinstance(fixtures, list)
    fixture = fixtures[0]
    assert isinstance(fixture, dict)
    partial = {
        "fixture_id": "fixture-one",
        "status": "SUCCEEDED",
        "reason_code": "INTEGRITY_OK",
        "file": {
            "sha256": fixture["sha256"],
            "size_bytes": fixture["size_bytes"],
        },
        "ground_truth": {
            "sha256": fixture["ground_truth_sha256"],
            "size_bytes": fixture["ground_truth_size_bytes"],
        },
    }

    def fail_after_result(
        _repo_root: Path,
        _prepared: object,
        _deadline: float,
        on_result: object,
    ) -> list[dict[str, object]]:
        assert callable(on_result)
        on_result(partial)
        raise HarnessError("INTEGRITY_MISMATCH", "synthetic integrity failure")

    monkeypatch.setattr("erp_docflow_experiment.runner.run_candidate", fail_after_result)
    requested = Path(".artifacts/experiments/partial-failure")

    with pytest.raises(HarnessError):
        run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)

    output = synthetic_repo.root / requested
    record = _load(output / "benchmark-run.json")
    assert record["status"] == "FAILED"
    assert record["succeeded_fixture_count"] == 1
    assert _load(output / "fixture-results.json") == {"results": [partial]}


def test_serialization_and_integrity_results_are_stable_between_runs(
    synthetic_repo: SyntheticRepository,
) -> None:
    first = Path(".artifacts/experiments/stable-one")
    second = Path(".artifacts/experiments/stable-two")
    run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, first)
    run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, second)
    first_root = synthetic_repo.root / first
    second_root = synthetic_repo.root / second

    assert (first_root / "fixture-results.json").read_bytes() == (
        second_root / "fixture-results.json"
    ).read_bytes()
    assert (first_root / "experiment-manifest.json").read_bytes() == (
        second_root / "experiment-manifest.json"
    ).read_bytes()
    for path in (first_root / "fixture-results.json", first_root / "experiment-manifest.json"):
        assert path.read_bytes().endswith(b"\n")
        assert b"\n " not in path.read_bytes()


def test_provenance_and_structured_logs_do_not_copy_secrets_content_or_absolute_paths(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_values = (
        "secret-token-value",
        "postgresql://user:password@example.invalid/database",
    )
    monkeypatch.setenv("OPENAI_API_KEY", secret_values[0])
    monkeypatch.setenv("DATABASE_URL", secret_values[1])
    requested = Path(".artifacts/experiments/redaction")
    run_experiment(synthetic_repo.root, synthetic_repo.manifest_path, requested)
    output = synthetic_repo.root / requested

    log_and_provenance = (
        (output / "events.jsonl").read_text(encoding="utf-8")
        + (output / "benchmark-run.json").read_text(encoding="utf-8")
    )
    assert all(secret not in log_and_provenance for secret in secret_values)
    assert str(synthetic_repo.root) not in log_and_provenance
    assert "Synthetic Supplier" not in log_and_provenance
    assert "synthetic fixture bytes" not in log_and_provenance


def test_git_provenance_disables_repository_hooks_and_fsmonitor(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_command: list[str] = []
    observed_environment: dict[str, str] = {}

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed_command.extend(command)
        environment = kwargs["env"]
        assert isinstance(environment, dict)
        observed_environment.update(environment)
        return subprocess.CompletedProcess(command, 0, stdout="a" * 40 + "\n", stderr="")

    monkeypatch.setattr(
        "erp_docflow_experiment.runner.shutil.which",
        lambda *_args, **_kwargs: "/usr/bin/git",
    )
    monkeypatch.setattr("erp_docflow_experiment.runner.subprocess.run", fake_run)

    assert _git(synthetic_repo.root, "status", "--porcelain") == "a" * 40
    assert observed_command[:5] == [
        "/usr/bin/git",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
    ]
    assert observed_environment["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert observed_environment["GIT_CONFIG_NOSYSTEM"] == "1"


def test_cli_returns_one_machine_readable_success(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(synthetic_repo.root)

    exit_code = main(
        [
            "validate-manifest",
            "--manifest",
            "experiments/synthetic/v1alpha/smoke.json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert json.loads(captured.out)["status"] == "VALID"


def test_cli_returns_typed_nonzero_failure_without_success_output(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifest = synthetic_repo.manifest_copy()
    candidate = manifest["candidate"]
    assert isinstance(candidate, dict)
    candidate["id"] = "unknown/v1"
    synthetic_repo.write_manifest(manifest)
    monkeypatch.chdir(synthetic_repo.root)

    exit_code = main(
        [
            "validate-manifest",
            "--manifest",
            "experiments/synthetic/v1alpha/smoke.json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error["status"] == "FAILED"
    assert error["reason_code"] == "CANDIDATE_NOT_REGISTERED"


def test_cli_redacts_unexpected_failure_without_traceback_or_secret(
    synthetic_repo: SyntheticRepository,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret = "unexpected-secret-that-must-not-leak"

    def fail_validation(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError(secret)

    monkeypatch.setattr("erp_docflow_experiment.cli.validate_experiment", fail_validation)
    monkeypatch.chdir(synthetic_repo.root)

    exit_code = main(
        [
            "validate-manifest",
            "--manifest",
            "experiments/synthetic/v1alpha/smoke.json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert secret not in captured.err
    assert "Traceback" not in captured.err
    assert json.loads(captured.err) == {
        "status": "FAILED",
        "reason_code": "HARNESS_INTERNAL_ERROR",
        "message": "experiment harness failed unexpectedly",
    }
