"""Strict JSON and hashing helpers shared by the harness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from erp_docflow_experiment.errors import HarnessError


def expect_object(value: object, context: str) -> dict[str, object]:
    """Return a JSON object or fail with a stable reason code."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise HarnessError("SCHEMA_INVALID", f"{context} must be a JSON object")
    return cast(dict[str, object], value)


def expect_list(value: object, context: str) -> list[object]:
    """Return a JSON array or fail with a stable reason code."""

    if not isinstance(value, list):
        raise HarnessError("SCHEMA_INVALID", f"{context} must be a JSON array")
    return cast(list[object], value)


def expect_string(value: object, context: str) -> str:
    """Return a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise HarnessError("SCHEMA_INVALID", f"{context} must be a non-empty string")
    return value


def expect_int(value: object, context: str) -> int:
    """Return a JSON integer, explicitly rejecting booleans."""

    if type(value) is not int:
        raise HarnessError("SCHEMA_INVALID", f"{context} must be an integer")
    return value


def expect_bool(value: object, context: str) -> bool:
    """Return a JSON boolean."""

    if type(value) is not bool:
        raise HarnessError("SCHEMA_INVALID", f"{context} must be a boolean")
    return value


def reject_unknown_keys(value: dict[str, object], allowed: set[str], context: str) -> None:
    """Fail closed when a contract contains an undeclared field."""

    unknown = sorted(set(value) - allowed)
    if unknown:
        raise HarnessError(
            "SCHEMA_INVALID",
            f"{context} contains unsupported fields: {', '.join(unknown)}",
        )


def require_keys(value: dict[str, object], required: set[str], context: str) -> None:
    """Fail closed when a required contract field is missing."""

    missing = sorted(required - set(value))
    if missing:
        raise HarnessError(
            "SCHEMA_INVALID",
            f"{context} is missing required fields: {', '.join(missing)}",
        )


def load_json_object(path: Path, context: str) -> dict[str, object]:
    """Load UTF-8 JSON while normalizing parser failures."""

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HarnessError("INPUT_READ_FAILED", f"cannot read {context}") from exc
    try:
        parsed = cast(object, json.loads(raw))
    except json.JSONDecodeError as exc:
        raise HarnessError("JSON_INVALID", f"{context} is not valid JSON") from exc
    return expect_object(parsed, context)


def canonical_json_bytes(value: object) -> bytes:
    """Serialize JSON deterministically for files and digests."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def write_canonical_json(path: Path, value: object) -> None:
    """Write one canonical JSON document."""

    try:
        path.write_bytes(canonical_json_bytes(value))
    except OSError as exc:
        raise HarnessError(
            "ARTIFACT_WRITE_FAILED",
            "cannot write an evidence artifact",
        ) from exc


def sha256_file(path: Path) -> tuple[str, int]:
    """Hash a file incrementally and return digest plus byte count."""

    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
    except OSError as exc:
        raise HarnessError("INPUT_READ_FAILED", "cannot read an input artifact") from exc
    return digest.hexdigest(), size
