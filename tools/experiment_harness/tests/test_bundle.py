"""Artifact bundle schema and tamper-detection tests."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

import erp_docflow_experiment.bundle as bundle_module
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


def test_created_bundle_digest_anchors_the_exact_descriptor_bytes(tmp_path: Path) -> None:
    root = tmp_path / "created-bundle"
    root.mkdir()
    for name in (
        "benchmark-run.json",
        "events.jsonl",
        "experiment-manifest.json",
        "fixture-results.json",
    ):
        (root / name).write_text("{}\n", encoding="utf-8")

    _, bundle_sha256 = create_bundle(
        root,
        "pytest-bundle",
        "2026-08-02T12:00:00Z",
    )

    assert bundle_sha256 == hashlib.sha256(
        (root / BUNDLE_FILENAME).read_bytes()
    ).hexdigest()


def test_verified_digest_uses_the_same_descriptor_snapshot_that_was_parsed(
    evidence_bundle: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    descriptor = evidence_bundle / BUNDLE_FILENAME
    original_bytes = descriptor.read_bytes()
    original_loader = bundle_module.load_json_object_with_bytes

    def load_then_mutate(
        path: Path,
        context: str,
        *,
        confinement_root: Path | None = None,
    ) -> tuple[dict[str, object], bytes]:
        value, raw = original_loader(
            path,
            context,
            confinement_root=confinement_root,
        )
        descriptor.write_bytes(raw + b" ")
        return value, raw

    monkeypatch.setattr(
        bundle_module,
        "load_json_object_with_bytes",
        load_then_mutate,
    )

    result = verify_bundle(evidence_bundle)

    assert result["bundle_sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert result["bundle_sha256"] != hashlib.sha256(descriptor.read_bytes()).hexdigest()


def test_four_noncanonical_files_cannot_form_an_evidence_bundle(tmp_path: Path) -> None:
    root = tmp_path / "arbitrary-bundle"
    root.mkdir()
    for index in range(4):
        (root / f"arbitrary-{index}.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(HarnessError) as caught:
        create_bundle(root, "pytest-bundle", "2026-08-02T12:00:00Z")

    assert _reason(caught) == "ARTIFACT_BUNDLE_INCOMPLETE"
    assert not (root / BUNDLE_FILENAME).exists()


def test_descriptor_cannot_replace_a_required_artifact_with_an_arbitrary_file(
    evidence_bundle: Path,
) -> None:
    descriptor = evidence_bundle / BUNDLE_FILENAME
    value = load_json_object(descriptor, "test bundle")
    files = value["files"]
    assert isinstance(files, list)
    events = next(
        item for item in files if isinstance(item, dict) and item.get("path") == "events.jsonl"
    )
    assert isinstance(events, dict)
    (evidence_bundle / "events.jsonl").rename(evidence_bundle / "replacement.jsonl")
    events["path"] = "replacement.jsonl"
    write_canonical_json(descriptor, value)

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "ARTIFACT_MISSING"


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


def test_symlink_swap_between_resolution_and_open_is_rejected(
    evidence_bundle: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    outside = tmp_path / "outside-secret.txt"
    outside.write_text("sensitive bytes", encoding="utf-8")
    original_hash = bundle_module.sha256_file
    swapped = False

    def swap_before_open(
        path: Path,
        deadline: float | None = None,
        *,
        confinement_root: Path | None = None,
    ) -> tuple[str, int]:
        nonlocal swapped
        if path.name == "events.jsonl" and not swapped:
            path.unlink()
            path.symlink_to(outside)
            swapped = True
        return original_hash(
            path,
            deadline,
            confinement_root=confinement_root,
        )

    monkeypatch.setattr(bundle_module, "sha256_file", swap_before_open)

    with pytest.raises(HarnessError) as caught:
        verify_bundle(evidence_bundle)

    assert _reason(caught) == "INPUT_READ_FAILED"


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
