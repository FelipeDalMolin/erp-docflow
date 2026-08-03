"""Experiment execution, provenance capture and evidence materialization."""

from __future__ import annotations

import os
import platform
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
    sha256_file,
    write_canonical_json,
)
from erp_docflow_experiment.manifest import PreparedExperiment, prepare_experiment
from erp_docflow_experiment.repository import repo_relative, resolve_output_directory


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git(repo_root: Path, *arguments: str) -> str:
    executable = shutil.which("git", path=os.defpath)
    if executable is None:
        raise HarnessError("PROVENANCE_UNAVAILABLE", "cannot capture Git provenance")
    try:
        completed = subprocess.run(
            [executable, *arguments],
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


def _peak_rss_bytes() -> int:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(peak)
    return int(peak * 1024)


def _environment() -> dict[str, object]:
    memory_total, memory_available = _memory_bytes()
    return {
        "host_class": "small-cpu-lab",
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "cpu": platform.processor() or "unknown",
        "logical_cpu_count": os.cpu_count(),
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


def _write_events(path: Path, events: list[dict[str, object]]) -> None:
    try:
        path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    except OSError as exc:
        raise HarnessError(
            "ARTIFACT_WRITE_FAILED",
            "cannot write an evidence artifact",
        ) from exc


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
        "succeeded_fixture_count": len(results),
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
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir()
    except FileExistsError as exc:
        raise HarnessError("OUTPUT_ALREADY_EXISTS", "output bundle already exists") from exc
    except OSError as exc:
        raise HarnessError("OUTPUT_CREATE_FAILED", "cannot create output bundle") from exc

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
    write_canonical_json(output / "experiment-manifest.json", prepared.manifest_value)

    try:
        deadline = started + prepared.manifest.controls.timeout_seconds
        candidate_results = run_candidate(repo_root, prepared, deadline, results.append)
        if candidate_results != results:
            raise HarnessError(
                "CANDIDATE_RESULT_INVALID",
                "candidate result callback diverged from returned results",
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
    except Exception:
        failure = HarnessError(
            "CANDIDATE_EXECUTION_FAILED",
            "candidate execution failed",
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
            succeeded_fixture_count=len(results),
        )
    )
    write_canonical_json(output / "fixture-results.json", {"results": results})
    write_canonical_json(output / "benchmark-run.json", record)
    _write_events(output / "events.jsonl", events)
    bundle = create_bundle(output, prepared.manifest.experiment_id, finished_at)

    if failure is not None:
        raise failure
    files = bundle.get("files")
    artifact_count = len(files) if isinstance(files, list) else 0
    bundle_sha256, _ = sha256_file(output / "artifact-bundle.json")
    return {
        "status": "SUCCEEDED",
        "experiment_id": prepared.manifest.experiment_id,
        "selected_fixture_count": len(results),
        "artifact_count": artifact_count,
        "bundle_sha256": bundle_sha256,
        "output": repo_relative(repo_root, output),
    }
