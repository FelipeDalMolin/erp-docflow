"""Experiment execution, provenance capture and evidence materialization."""

from __future__ import annotations

import os
import platform
import re
import resource
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from erp_docflow_experiment import __version__
from erp_docflow_experiment.bundle import create_bundle
from erp_docflow_experiment.candidates import run_candidate
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import (
    canonical_json_bytes,
    expect_int,
    expect_object,
    expect_string,
    reject_unknown_keys,
    require_keys,
    write_new_canonical_json,
    write_new_file_bytes,
)
from erp_docflow_experiment.manifest import PreparedExperiment, prepare_experiment
from erp_docflow_experiment.repository import (
    assert_directory_identity,
    create_staging_directory,
    publish_staging_directory,
    repo_relative,
    resolve_output_directory,
)

_REASON_CODE_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,127}")
_DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git(repo_root: Path, *arguments: str) -> str:
    executable = shutil.which("git", path=os.defpath)
    if executable is None:
        raise HarnessError("PROVENANCE_UNAVAILABLE", "cannot capture Git provenance")
    try:
        completed = subprocess.run(
            [
                executable,
                "-c",
                "core.fsmonitor=false",
                "-c",
                "core.hooksPath=/dev/null",
                *arguments,
            ],
            cwd=repo_root,
            check=False,
            capture_output=True,
            env={
                "GIT_CONFIG_GLOBAL": "/dev/null",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_OPTIONAL_LOCKS": "0",
                "LC_ALL": "C.UTF-8",
                "PATH": os.defpath,
            },
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HarnessError("PROVENANCE_UNAVAILABLE", "cannot capture Git provenance") from exc
    if completed.returncode != 0:
        raise HarnessError("PROVENANCE_UNAVAILABLE", "cannot capture Git provenance")
    return completed.stdout.strip()


def _memory_bytes() -> tuple[int | None, int | None]:
    """Read Linux total/available memory without recording process environment values."""

    try:
        lines = Path("/proc/meminfo").read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError):
        return None, None
    values: dict[str, int] = {}
    for line in lines:
        fields = line.split()
        if len(fields) == 3 and fields[0] in {"MemTotal:", "MemAvailable:"}:
            try:
                value = int(fields[1]) * 1024 if fields[2] == "kB" else 0
            except ValueError:
                continue
            if value > 0:
                values[fields[0]] = value
    return values.get("MemTotal:"), values.get("MemAvailable:")


def _cpu_model() -> str:
    """Capture one allowlisted CPU model fact with a portable architecture fallback."""

    try:
        lines = Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        lines = []
    for line in lines:
        key, separator, value = line.partition(":")
        if separator and key.strip() in {"model name", "Hardware", "Processor"}:
            model = value.strip()
            if model:
                return model[:512]
    processor = platform.processor().strip()
    if processor:
        return processor[:512]
    architecture = platform.machine().strip() or "unavailable"
    return f"architecture:{architecture}"[:512]


def _host_class(logical_cpu_count: int | None, memory_total_bytes: int | None) -> str:
    """Derive a comparison-safe observed resource class without claiming target eligibility."""

    cpu = str(logical_cpu_count) if logical_cpu_count and logical_cpu_count > 0 else "unknown"
    if memory_total_bytes and memory_total_bytes > 0:
        gibibyte = 1024**3
        rounded_gib = max(1, (memory_total_bytes + gibibyte // 2) // gibibyte)
        memory = f"{rounded_gib}gib"
    else:
        memory = "unknown"
    return f"observed-cpu-{cpu}-memory-{memory}-gpu-not-declared"


def _peak_rss_bytes() -> int:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(peak)
    return int(peak * 1024)


def _environment() -> dict[str, object]:
    memory_total, memory_available = _memory_bytes()
    logical_cpu_count = os.cpu_count()
    return {
        "host_class": _host_class(logical_cpu_count, memory_total),
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "cpu": _cpu_model(),
        "logical_cpu_count": logical_cpu_count,
        "memory_total_bytes": memory_total,
        "memory_available_bytes": memory_available,
        "gpu": "not_declared",
        "runtime_versions": {
            "python": platform.python_version(),
            "harness": __version__,
        },
    }


def _provenance(repo_root: Path, prepared: PreparedExperiment, output: Path) -> dict[str, object]:
    manifest_ref = repo_relative(repo_root, prepared.manifest_path)
    output_ref = repo_relative(repo_root, output)
    git_root = Path(_git(repo_root, "rev-parse", "--show-toplevel")).resolve()
    if git_root != repo_root.resolve():
        raise HarnessError("PROVENANCE_UNAVAILABLE", "Git root does not match repository")
    return {
        "git_commit": _git(repo_root, "rev-parse", "HEAD"),
        "workspace_clean": not bool(
            _git(repo_root, "status", "--porcelain", "--untracked-files=all")
        ),
        "input_sha256": prepared.input_digests,
        "runner_version": __version__,
        "runner_command": (
            "erp-docflow-experiment run "
            f"--manifest {manifest_ref} --output {output_ref}"
        ),
    }


def _event(event: str, **fields: object) -> dict[str, object]:
    return {"timestamp": _utc_now(), "event": event, **fields}


def _write_events(
    path: Path,
    events: list[dict[str, object]],
    *,
    confinement_root: Path,
) -> None:
    write_new_file_bytes(
        path,
        b"".join(canonical_json_bytes(event) for event in events),
        confinement_root=confinement_root,
    )


def validate_experiment(repo_root: Path, manifest_path: Path) -> dict[str, object]:
    """Validate a manifest and every static reference without executing a candidate."""

    prepared = prepare_experiment(repo_root, manifest_path)
    return {
        "status": "VALID",
        "schema_version": prepared.manifest.schema_version,
        "experiment_id": prepared.manifest.experiment_id,
        "candidate": prepared.manifest.candidate.candidate_id,
        "selected_fixture_count": len(prepared.selected_fixtures),
        "dataset_classification": prepared.manifest.dataset_classification,
    }


def _validate_digest_fact(value: object, context: str) -> tuple[str, int]:
    fact = expect_object(value, context)
    keys = {"sha256", "size_bytes"}
    require_keys(fact, keys, context)
    reject_unknown_keys(fact, keys, context)
    digest = expect_string(fact.get("sha256"), f"{context}.sha256")
    size = expect_int(fact.get("size_bytes"), f"{context}.size_bytes")
    if _DIGEST_PATTERN.fullmatch(digest) is None or size < 0:
        raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate emitted invalid facts")
    return digest, size


def _validate_candidate_results(
    prepared: PreparedExperiment,
    results: list[dict[str, object]],
    *,
    require_complete_success: bool,
) -> None:
    """Accept only an ordered, allowlisted result prefix for the registered probe."""

    expected_ids = [
        expect_string(fixture.get("id"), "selected fixture ID")
        for fixture in prepared.selected_fixtures
    ]
    if len(results) > len(expected_ids):
        raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate emitted too many results")

    for index, raw_result in enumerate(results):
        selected_fixture = prepared.selected_fixtures[index]
        result = expect_object(raw_result, "candidate result")
        common_keys = {"fixture_id", "status", "reason_code"}
        require_keys(result, common_keys, "candidate result")
        fixture_id = expect_string(result.get("fixture_id"), "candidate result fixture ID")
        status = expect_string(result.get("status"), "candidate result status")
        reason_code = expect_string(result.get("reason_code"), "candidate result reason code")
        if fixture_id != expected_ids[index] or _REASON_CODE_PATTERN.fullmatch(reason_code) is None:
            raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate emitted invalid facts")

        if status == "SUCCEEDED":
            success_keys = common_keys | {"file", "ground_truth"}
            require_keys(result, success_keys, "candidate result")
            reject_unknown_keys(result, success_keys, "candidate result")
            file_digest, file_size = _validate_digest_fact(
                result.get("file"),
                "candidate result file",
            )
            ground_truth_digest, ground_truth_size = _validate_digest_fact(
                result.get("ground_truth"),
                "candidate result ground truth",
            )
            expected_file = (
                expect_string(selected_fixture.get("sha256"), "selected fixture digest"),
                expect_int(selected_fixture.get("size_bytes"), "selected fixture size"),
            )
            expected_ground_truth = (
                expect_string(
                    selected_fixture.get("ground_truth_sha256"),
                    "selected ground truth digest",
                ),
                expect_int(
                    selected_fixture.get("ground_truth_size_bytes"),
                    "selected ground truth size",
                ),
            )
            if reason_code != "INTEGRITY_OK":
                raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate emitted invalid facts")
            if (file_digest, file_size) != expected_file or (
                ground_truth_digest,
                ground_truth_size,
            ) != expected_ground_truth:
                raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate emitted invalid facts")
        elif status == "FAILED" and not require_complete_success:
            reject_unknown_keys(result, common_keys, "candidate result")
        else:
            raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate did not fully succeed")

    if require_complete_success and len(results) != len(expected_ids):
        raise HarnessError("CANDIDATE_RESULT_INVALID", "candidate returned incomplete results")


def _run_record(
    prepared: PreparedExperiment,
    provenance: dict[str, object],
    environment: dict[str, object],
    started_at: str,
    finished_at: str,
    duration_seconds: float,
    results: list[dict[str, object]],
    failure: HarnessError | None,
) -> dict[str, object]:
    manifest = prepared.manifest
    succeeded_fixture_count = sum(
        result.get("status") == "SUCCEEDED" for result in results
    )
    return {
        "schema_version": "benchmark-run/v1alpha",
        "experiment_id": manifest.experiment_id,
        "issue": manifest.issue,
        "capability": manifest.capability,
        "candidate": manifest.candidate.candidate_id,
        "status": "FAILED" if failure else "SUCCEEDED",
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(duration_seconds, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "selected_fixture_count": len(prepared.selected_fixtures),
        "succeeded_fixture_count": succeeded_fixture_count,
        "failure": (
            {"reason_code": failure.reason_code, "message": failure.message}
            if failure
            else None
        ),
        "provenance": provenance,
        "environment": environment,
        "controls": {
            "runtime_egress_allowed": manifest.controls.runtime_egress_allowed,
            "real_data_allowed": manifest.controls.real_data_allowed,
            "max_parallel_jobs": manifest.controls.max_parallel_jobs,
            "timeout_seconds": manifest.controls.timeout_seconds,
            "random_seed": manifest.controls.random_seed,
        },
        "artifacts": {
            "resolved_manifest": "experiment-manifest.json",
            "fixture_results": "fixture-results.json",
            "events": "events.jsonl",
        },
    }


def run_experiment(
    repo_root: Path,
    manifest_path: Path,
    requested_output: Path,
) -> dict[str, object]:
    """Execute one validated experiment and always preserve materialized failure evidence."""

    prepared = prepare_experiment(repo_root, manifest_path)
    output = resolve_output_directory(repo_root, requested_output)
    provenance = _provenance(repo_root, prepared, output)
    environment = _environment()
    staging, staging_identity = create_staging_directory(repo_root, output)

    started_at = _utc_now()
    started = time.monotonic()
    events = [
        _event(
            "experiment_started",
            experiment_id=prepared.manifest.experiment_id,
            candidate=prepared.manifest.candidate.candidate_id,
            selected_fixture_count=len(prepared.selected_fixtures),
        )
    ]
    results: list[dict[str, object]] = []
    failure: HarnessError | None = None
    write_new_canonical_json(
        staging / "experiment-manifest.json",
        prepared.manifest_value,
        confinement_root=staging,
    )

    try:
        deadline = started + prepared.manifest.controls.timeout_seconds
        candidate_results = run_candidate(repo_root, prepared, deadline, results.append)
        if candidate_results != results:
            raise HarnessError(
                "CANDIDATE_RESULT_INVALID",
                "candidate result callback diverged from returned results",
            )
        _validate_candidate_results(
            prepared,
            results,
            require_complete_success=True,
        )
        events.append(
            _event(
                "candidate_succeeded",
                fixture_count=len(results),
                reason_code="INTEGRITY_OK",
            )
        )
    except HarnessError as exc:
        failure = exc
        events.append(_event("candidate_failed", reason_code=exc.reason_code))
    except KeyboardInterrupt:
        failure = HarnessError(
            "OPERATOR_INTERRUPTED",
            "experiment interrupted by operator",
        )
        events.append(_event("candidate_failed", reason_code=failure.reason_code))
    except Exception:
        failure = HarnessError(
            "CANDIDATE_EXECUTION_FAILED",
            "candidate execution failed",
        )
        events.append(_event("candidate_failed", reason_code=failure.reason_code))

    try:
        _validate_candidate_results(
            prepared,
            results,
            require_complete_success=False,
        )
    except HarnessError:
        results.clear()
        if failure is None or failure.reason_code != "CANDIDATE_RESULT_INVALID":
            failure = HarnessError(
                "CANDIDATE_RESULT_INVALID",
                "candidate emitted invalid or unsafe results",
            )
            events.append(_event("candidate_failed", reason_code=failure.reason_code))

    finished_at = _utc_now()
    duration = time.monotonic() - started
    record = _run_record(
        prepared,
        provenance,
        environment,
        started_at,
        finished_at,
        duration,
        results,
        failure,
    )
    events.append(
        _event(
            "experiment_finished",
            status=record["status"],
            succeeded_fixture_count=record["succeeded_fixture_count"],
        )
    )
    write_new_canonical_json(
        staging / "fixture-results.json",
        {"results": results},
        confinement_root=staging,
    )
    write_new_canonical_json(
        staging / "benchmark-run.json",
        record,
        confinement_root=staging,
    )
    _write_events(
        staging / "events.jsonl",
        events,
        confinement_root=staging,
    )
    bundle, bundle_sha256 = create_bundle(
        staging,
        prepared.manifest.experiment_id,
        finished_at,
    )
    assert_directory_identity(staging, staging_identity)
    publish_staging_directory(staging, staging_identity, output)

    if failure is not None:
        raise failure
    files = bundle.get("files")
    artifact_count = len(files) if isinstance(files, list) else 0
    return {
        "status": "SUCCEEDED",
        "experiment_id": prepared.manifest.experiment_id,
        "selected_fixture_count": len(results),
        "artifact_count": artifact_count,
        "bundle_sha256": bundle_sha256,
        "output": repo_relative(repo_root, output),
    }
