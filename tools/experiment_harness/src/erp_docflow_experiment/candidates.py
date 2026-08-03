"""Closed candidate registry and the non-promotable integrity probe."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import expect_int, expect_string, sha256_file
from erp_docflow_experiment.manifest import PreparedExperiment
from erp_docflow_experiment.repository import resolve_dataset_file


def _verify_digest(
    path: Path,
    expected_sha256: str,
    expected_size: int,
    deadline: float,
    confinement_root: Path,
) -> tuple[str, int]:
    actual_sha256, actual_size = sha256_file(
        path,
        deadline,
        confinement_root=confinement_root,
    )
    if actual_sha256 != expected_sha256 or actual_size != expected_size:
        raise HarnessError("INTEGRITY_MISMATCH", "an input digest or size does not match")
    return actual_sha256, actual_size


def run_integrity_probe(
    repo_root: Path,
    prepared: PreparedExperiment,
    deadline: float,
    on_result: Callable[[dict[str, object]], None] | None = None,
) -> list[dict[str, object]]:
    """Read real fixture bytes and verify dataset plus ground-truth integrity."""

    dataset_directory = prepared.dataset_manifest_path.parent
    results: list[dict[str, object]] = []
    for fixture in prepared.selected_fixtures:
        fixture_id = expect_string(fixture.get("id"), "fixture.id")
        try:
            if time.monotonic() > deadline:
                raise HarnessError("TIMEOUT_EXCEEDED", "candidate exceeded its timeout")

            file_path = resolve_dataset_file(
                repo_root,
                dataset_directory,
                expect_string(fixture.get("path"), "fixture.path"),
                "fixture.path",
            )
            file_sha256, file_size = _verify_digest(
                file_path,
                expect_string(fixture.get("sha256"), "fixture.sha256"),
                expect_int(fixture.get("size_bytes"), "fixture.size_bytes"),
                deadline,
                dataset_directory,
            )

            ground_truth_path = resolve_dataset_file(
                repo_root,
                dataset_directory,
                expect_string(
                    fixture.get("ground_truth"),
                    "fixture.ground_truth",
                ),
                "fixture.ground_truth",
            )
            ground_truth_sha256, ground_truth_size = _verify_digest(
                ground_truth_path,
                expect_string(
                    fixture.get("ground_truth_sha256"),
                    "fixture.ground_truth_sha256",
                ),
                expect_int(
                    fixture.get("ground_truth_size_bytes"),
                    "fixture.ground_truth_size_bytes",
                ),
                deadline,
                dataset_directory,
            )
        except HarnessError as exc:
            failed_result: dict[str, object] = {
                "fixture_id": fixture_id,
                "status": "FAILED",
                "reason_code": exc.reason_code,
            }
            results.append(failed_result)
            if on_result is not None:
                on_result(failed_result)
            raise

        result: dict[str, object] = {
            "fixture_id": fixture_id,
            "status": "SUCCEEDED",
            "reason_code": "INTEGRITY_OK",
            "file": {"sha256": file_sha256, "size_bytes": file_size},
            "ground_truth": {
                "sha256": ground_truth_sha256,
                "size_bytes": ground_truth_size,
            },
        }
        results.append(result)
        if on_result is not None:
            on_result(result)
    return results


def run_candidate(
    repo_root: Path,
    prepared: PreparedExperiment,
    deadline: float,
    on_result: Callable[[dict[str, object]], None] | None = None,
) -> list[dict[str, object]]:
    """Dispatch only through the closed, code-owned candidate registry."""

    if prepared.manifest.candidate.candidate_id == "integrity_probe/v1":
        return run_integrity_probe(repo_root, prepared, deadline, on_result)
    raise HarnessError("CANDIDATE_NOT_REGISTERED", "candidate is not in the closed registry")
