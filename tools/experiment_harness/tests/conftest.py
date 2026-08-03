"""Hermetic fixtures for the experiment harness test suite."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import pytest


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


@dataclass
class SyntheticRepository:
    """A minimal committed repository accepted by the real harness code."""

    root: Path
    manifest_path: Path
    dataset_path: Path
    fixture_path: Path
    ground_truth_path: Path
    manifest: dict[str, object]
    dataset: dict[str, object]

    def write_manifest(self, value: dict[str, object] | None = None) -> Path:
        _write_json(self.manifest_path, value if value is not None else self.manifest)
        return self.manifest_path

    def write_dataset(self, value: dict[str, object] | None = None) -> Path:
        _write_json(self.dataset_path, value if value is not None else self.dataset)
        return self.dataset_path

    def manifest_copy(self) -> dict[str, object]:
        return deepcopy(self.manifest)

    def dataset_copy(self) -> dict[str, object]:
        return deepcopy(self.dataset)


@pytest.fixture
def synthetic_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> SyntheticRepository:
    """Create one real-byte synthetic dataset in an isolated Git repository."""

    root = tmp_path / "repository"
    root.mkdir()
    (root / ".gitignore").write_text(".artifacts/experiments/\n", encoding="utf-8")

    fixture_bytes = b"%PDF-1.4\nsynthetic fixture bytes\n%%EOF\n"
    ground_truth_value = {
        "fixture_id": "fixture-one",
        "fields": {"issuer_name": "Synthetic Supplier"},
    }
    ground_truth_bytes = (
        json.dumps(
            ground_truth_value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()

    dataset_directory = root / "datasets" / "synthetic" / "v1alpha"
    fixture_path = dataset_directory / "files" / "fixture-one.pdf"
    ground_truth_path = dataset_directory / "ground_truth" / "fixture-one.json"
    fixture_path.parent.mkdir(parents=True)
    ground_truth_path.parent.mkdir(parents=True)
    fixture_path.write_bytes(fixture_bytes)
    ground_truth_path.write_bytes(ground_truth_bytes)

    dataset: dict[str, object] = {
        "classification": "synthetic",
        "profile_ref": "profiles/synthetic/v1alpha/profile.json",
        "fixtures": [
            {
                "id": "fixture-one",
                "split": "test",
                "path": "files/fixture-one.pdf",
                "sha256": _sha256(fixture_bytes),
                "size_bytes": len(fixture_bytes),
                "ground_truth": "ground_truth/fixture-one.json",
                "ground_truth_sha256": _sha256(ground_truth_bytes),
                "ground_truth_size_bytes": len(ground_truth_bytes),
            }
        ],
    }
    dataset_path = dataset_directory / "manifest.json"
    _write_json(dataset_path, dataset)

    profile_path = root / "profiles" / "synthetic" / "v1alpha" / "profile.json"
    _write_json(
        profile_path,
        {
            "data_classification": "synthetic",
            "benchmark": {
                "dataset_manifest": "datasets/synthetic/v1alpha/manifest.json",
                "acceptance_policy": "benchmarks/synthetic/v1alpha/acceptance.json",
            },
        },
    )
    acceptance_path = root / "benchmarks" / "synthetic" / "v1alpha" / "acceptance.json"
    _write_json(
        acceptance_path,
        {"dataset_manifest": "datasets/synthetic/v1alpha/manifest.json"},
    )
    lock_path = root / "tools" / "experiment_harness" / "uv.lock"
    lock_path.parent.mkdir(parents=True)
    lock_path.write_text("version = 1\n", encoding="utf-8")

    manifest: dict[str, object] = {
        "schema_version": "experiment-manifest/v1alpha",
        "experiment_id": "pytest-integrity-probe",
        "issue": 88,
        "purpose": "Exercise the harness with synthetic bytes.",
        "capability": "harness_integrity",
        "profile_ref": "profiles/synthetic/v1alpha/profile.json",
        "dataset_manifest_ref": "datasets/synthetic/v1alpha/manifest.json",
        "acceptance_policy_ref": "benchmarks/synthetic/v1alpha/acceptance.json",
        "dependency_lock_ref": "tools/experiment_harness/uv.lock",
        "dataset_classification": "synthetic",
        "candidate": {
            "id": "integrity_probe/v1",
            "configuration": {"verify_ground_truth": True},
        },
        "controls": {
            "runtime_egress_allowed": False,
            "real_data_allowed": False,
            "max_parallel_jobs": 1,
            "timeout_seconds": 30,
            "random_seed": 20260731,
        },
        "fixture_selector": {
            "splits": ["test"],
            "fixture_ids": [],
            "expected_fixture_count": 1,
        },
    }
    manifest_path = root / "experiments" / "synthetic" / "v1alpha" / "smoke.json"
    _write_json(manifest_path, manifest)

    (root / ".git").mkdir()

    def fake_git(_repo: Path, *arguments: str) -> str:
        if arguments == ("rev-parse", "--show-toplevel"):
            return str(root)
        if arguments == ("rev-parse", "HEAD"):
            return "a" * 40
        if arguments == ("status", "--porcelain", "--untracked-files=all"):
            return ""
        raise AssertionError(f"unexpected Git invocation: {arguments}")

    monkeypatch.setattr("erp_docflow_experiment.runner._git", fake_git)

    return SyntheticRepository(
        root=root,
        manifest_path=manifest_path,
        dataset_path=dataset_path,
        fixture_path=fixture_path,
        ground_truth_path=ground_truth_path,
        manifest=manifest,
        dataset=dataset,
    )
