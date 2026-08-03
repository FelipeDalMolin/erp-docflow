"""Artifact bundle schema and tamper-detection tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from erp_docflow_experiment.bundle import BUNDLE_FILENAME, create_bundle, verify_bundle
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import load_json_object, write_canonical_json


@pytest.fixture
def evidence_bundle(tmp_path: Path) -> Path:
    root = tmp_path / "bundle"
    root.mkdir()
    for name, content in (
        ("benchmark-run.json", b"{}\n"),
        ("events.jsonl", b"{}\n"),
        ("experiment-manifest.json", b"{}\n"),
        ("fixture-results.json", b"{}\n"),
    ):
        (root / name).write_bytes(content)
    create_bundle(root, "pytest-bundle", "2026-08-02T12:00:00Z")
    return root


def _reason(error: pytest.ExceptionInfo[HarnessError]) -> str:
    return error.value.reason_code


def test_missing_artifact_is_rejected(evidence_bundle: Path) -> None:
    (evidence_bundle / "events.jsonl").unlink()

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_MISSING"


def test_extra_artifact_is_rejected(evidence_bundle: Path) -> None:
    (evidence_bundle / "uninventoried.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_EXTRA"


def test_changed_artifact_is_rejected(evidence_bundle: Path) -> None:
    (evidence_bundle / "events.jsonl").write_text('{"changed":true}\n', encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_INTEGRITY_MISMATCH"


def test_path_traversal_in_descriptor_is_rejected(evidence_bundle: Path) -> None:
    descriptor = evidence_bundle / BUNDLE_FILENAME
    value = load_json_object(descriptor, "test bundle")
    files = value["files"]
    assert isinstance(files, list)
    first = files[0]
    assert isinstance(first, dict)
    first["path"] = "../escape.json"
    write_canonical_json(descriptor, value)

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_PATH_INVALID"


def test_duplicate_inventory_path_is_rejected(evidence_bundle: Path) -> None:
    descriptor = evidence_bundle / BUNDLE_FILENAME
    value = load_json_object(descriptor, "test bundle")
    files = value["files"]
    assert isinstance(files, list)
    first = files[0]
    second = files[1]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    second["path"] = first["path"]
    write_canonical_json(descriptor, value)

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_DUPLICATE"


def test_symlink_artifact_is_rejected(evidence_bundle: Path) -> None:
    (evidence_bundle / "linked-artifact.json").symlink_to(
        evidence_bundle / "benchmark-run.json"
    )

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_PATH_INVALID"


def test_nested_descriptor_name_is_treated_as_an_extra_artifact(
    evidence_bundle: Path,
) -> None:
    nested = evidence_bundle / "nested"
    nested.mkdir()
    (nested / BUNDLE_FILENAME).write_text("{}\n", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_EXTRA"


def test_non_regular_artifact_is_rejected(evidence_bundle: Path) -> None:
    os.mkfifo(evidence_bundle / "unexpected-fifo")

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_PATH_INVALID"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [("sha256", "ABC"), ("size_bytes", -1), ("media_type", "not-a-media-type")],
)
def test_invalid_inventory_contract_is_rejected(
    evidence_bundle: Path,
    field: str,
    invalid_value: object,
) -> None:
    descriptor = evidence_bundle / BUNDLE_FILENAME
    value = load_json_object(descriptor, "test bundle")
    files = value["files"]
    assert isinstance(files, list)
    first = files[0]
    assert isinstance(first, dict)
    first[field] = invalid_value
    write_canonical_json(descriptor, value)

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "SCHEMA_INVALID"


def test_write_failures_are_typed(tmp_path: Path) -> None:
    with pytest.raises(HarnessError) as caught:
        write_canonical_json(tmp_path / "missing" / "artifact.json", {})

    assert _reason(caught) == "ARTIFACT_WRITE_FAILED"
