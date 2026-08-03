"""Artifact bundle creation and tamper detection."""

from __future__ import annotations

import mimetypes
import re
from datetime import datetime
from pathlib import Path

from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import (
    expect_int,
    expect_list,
    expect_object,
    expect_string,
    load_json_object,
    reject_unknown_keys,
    require_keys,
    sha256_file,
    write_canonical_json,
)
from erp_docflow_experiment.repository import safe_bundle_member

BUNDLE_FILENAME = "artifact-bundle.json"
BUNDLE_KEYS = {"schema_version", "experiment_id", "created_at", "files"}
ENTRY_KEYS = {"path", "sha256", "size_bytes", "media_type"}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
MEDIA_TYPE_PATTERN = re.compile(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+")
IDENTIFIER_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{2,127}")
ARTIFACT_PATH_PATTERN = re.compile(
    r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*"
)


def _media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def create_bundle(bundle_root: Path, experiment_id: str, created_at: str) -> dict[str, object]:
    """Inventory every regular evidence file and write the bundle descriptor last."""

    files: list[dict[str, object]] = []
    descriptor = bundle_root / BUNDLE_FILENAME
    for path in sorted(bundle_root.rglob("*")):
        if path == descriptor:
            continue
        if path.is_symlink():
            raise HarnessError("ARTIFACT_PATH_INVALID", "symlink artifacts are not allowed")
        if path.is_dir():
            continue
        if not path.is_file():
            raise HarnessError("ARTIFACT_PATH_INVALID", "bundle contains a non-regular artifact")
        digest, size = sha256_file(path)
        files.append(
            {
                "path": path.relative_to(bundle_root).as_posix(),
                "sha256": digest,
                "size_bytes": size,
                "media_type": _media_type(path),
            }
        )
    if len(files) < 4:
        raise HarnessError(
            "ARTIFACT_BUNDLE_INCOMPLETE",
            "bundle must contain the required evidence files",
        )
    value: dict[str, object] = {
        "schema_version": "artifact-bundle/v1alpha",
        "experiment_id": experiment_id,
        "created_at": created_at,
        "files": files,
    }
    write_canonical_json(descriptor, value)
    return value


def verify_bundle(bundle_root: Path) -> dict[str, object]:
    """Reject missing, changed, extra, duplicate or unsafe bundle members."""

    if not bundle_root.is_dir() or bundle_root.is_symlink():
        raise HarnessError("BUNDLE_NOT_FOUND", "bundle directory does not exist")
    descriptor = bundle_root / BUNDLE_FILENAME
    if descriptor.is_symlink() or not descriptor.is_file():
        raise HarnessError("BUNDLE_NOT_FOUND", "bundle descriptor does not exist")
    value = load_json_object(descriptor, "artifact bundle")
    require_keys(value, BUNDLE_KEYS, "artifact bundle")
    reject_unknown_keys(value, BUNDLE_KEYS, "artifact bundle")
    if value.get("schema_version") != "artifact-bundle/v1alpha":
        raise HarnessError("SCHEMA_VERSION_UNSUPPORTED", "unsupported bundle schema")
    experiment_id = expect_string(value.get("experiment_id"), "artifact_bundle.experiment_id")
    if IDENTIFIER_PATTERN.fullmatch(experiment_id) is None:
        raise HarnessError("SCHEMA_INVALID", "artifact bundle experiment ID is invalid")
    created_at = expect_string(value.get("created_at"), "artifact_bundle.created_at")
    try:
        timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HarnessError("SCHEMA_INVALID", "artifact bundle timestamp is invalid") from exc
    if timestamp.tzinfo is None:
        raise HarnessError("SCHEMA_INVALID", "artifact bundle timestamp requires a timezone")

    inventory = expect_list(value.get("files"), "artifact_bundle.files")
    if len(inventory) < 4:
        raise HarnessError("SCHEMA_INVALID", "artifact_bundle.files is incomplete")
    expected_paths: set[str] = set()
    for index, item in enumerate(inventory):
        entry = expect_object(item, f"artifact_bundle.files[{index}]")
        require_keys(entry, ENTRY_KEYS, f"artifact_bundle.files[{index}]")
        reject_unknown_keys(entry, ENTRY_KEYS, f"artifact_bundle.files[{index}]")
        member = expect_string(entry.get("path"), f"artifact_bundle.files[{index}].path")
        if (
            len(member) > 512
            or ARTIFACT_PATH_PATTERN.fullmatch(member) is None
            or member == BUNDLE_FILENAME
        ):
            raise HarnessError(
                "ARTIFACT_PATH_INVALID",
                "bundle contains an unsafe artifact path",
            )
        if member in expected_paths:
            raise HarnessError("ARTIFACT_DUPLICATE", "bundle inventory contains duplicates")
        expected_paths.add(member)
        path = safe_bundle_member(bundle_root, member)
        if path.is_symlink() or not path.is_file():
            raise HarnessError("ARTIFACT_MISSING", "an inventoried artifact is missing")
        actual_sha256, actual_size = sha256_file(path)
        expected_sha256 = expect_string(
            entry.get("sha256"),
            f"artifact_bundle.files[{index}].sha256",
        )
        if SHA256_PATTERN.fullmatch(expected_sha256) is None:
            raise HarnessError("SCHEMA_INVALID", "artifact digest must be lowercase SHA-256")
        expected_size = expect_int(
            entry.get("size_bytes"),
            f"artifact_bundle.files[{index}].size_bytes",
        )
        if expected_size < 0:
            raise HarnessError("SCHEMA_INVALID", "artifact size cannot be negative")
        media_type = expect_string(
            entry.get("media_type"),
            f"artifact_bundle.files[{index}].media_type",
        )
        if len(media_type) > 255 or MEDIA_TYPE_PATTERN.fullmatch(media_type) is None:
            raise HarnessError("SCHEMA_INVALID", "artifact media type is invalid")
        if actual_sha256 != expected_sha256 or actual_size != expected_size:
            raise HarnessError("ARTIFACT_INTEGRITY_MISMATCH", "an artifact was modified")

    actual_paths: set[str] = set()
    for path in bundle_root.rglob("*"):
        if path.is_symlink():
            raise HarnessError("ARTIFACT_PATH_INVALID", "symlink artifacts are not allowed")
        if path.is_dir():
            continue
        if not path.is_file():
            raise HarnessError(
                "ARTIFACT_PATH_INVALID",
                "bundle contains a non-regular artifact",
            )
        if path != descriptor:
            actual_paths.add(path.relative_to(bundle_root).as_posix())
    extras = sorted(actual_paths - expected_paths)
    missing = sorted(expected_paths - actual_paths)
    if missing:
        raise HarnessError("ARTIFACT_MISSING", "bundle is missing inventoried artifacts")
    if extras:
        raise HarnessError("ARTIFACT_EXTRA", "bundle contains uninventoried artifacts")
    bundle_sha256, _ = sha256_file(descriptor)
    return {
        "status": "VERIFIED",
        "experiment_id": experiment_id,
        "artifact_count": len(expected_paths),
        "bundle_sha256": bundle_sha256,
    }
