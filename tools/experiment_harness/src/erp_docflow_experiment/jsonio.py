"""Strict JSON and hashing helpers shared by the harness."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import time
from pathlib import Path
from typing import cast

from erp_docflow_experiment.errors import HarnessError

_DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_READ_FLAGS = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
_WRITE_NEW_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _open_absolute_directory(path: Path, context: str) -> int:
    """Open every directory component without following symlinks."""

    absolute = _absolute_lexical(path)
    descriptor: int | None = None
    try:
        descriptor = os.open(absolute.anchor, _DIRECTORY_FLAGS)
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except OSError as exc:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} contains an unsafe path") from exc
    assert descriptor is not None
    return descriptor


def _relative_beneath(path: Path, root: Path, context: str) -> tuple[Path, tuple[str, ...]]:
    absolute_path = _absolute_lexical(path)
    absolute_root = _absolute_lexical(root)
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} leaves its allowed root") from exc
    if not relative.parts or ".." in relative.parts:
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} is not a regular file path")
    return absolute_root, relative.parts


def _open_regular_file(path: Path, context: str, confinement_root: Path | None) -> int:
    root = confinement_root if confinement_root is not None else path.parent
    absolute_root, parts = _relative_beneath(path, root, context)
    directory_descriptor = _open_absolute_directory(absolute_root, context)
    try:
        for part in parts[:-1]:
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        descriptor = os.open(parts[-1], _READ_FLAGS, dir_fd=directory_descriptor)
    except OSError as exc:
        raise HarnessError("INPUT_READ_FAILED", f"cannot read {context}") from exc
    finally:
        os.close(directory_descriptor)
    try:
        metadata = os.fstat(descriptor)
    except OSError as exc:
        os.close(descriptor)
        raise HarnessError("INPUT_READ_FAILED", f"cannot read {context}") from exc
    if not stat.S_ISREG(metadata.st_mode):
        os.close(descriptor)
        raise HarnessError("INPUT_READ_FAILED", f"cannot read {context}")
    return descriptor


def _stable_metadata(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def read_file_bytes(
    path: Path,
    context: str,
    *,
    confinement_root: Path | None = None,
) -> bytes:
    """Read one stable regular-file snapshot without following path symlinks."""

    descriptor = _open_regular_file(path, context, confinement_root)
    chunks: list[bytes] = []
    try:
        before = os.fstat(descriptor)
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(descriptor)
    except OSError as exc:
        raise HarnessError("INPUT_READ_FAILED", f"cannot read {context}") from exc
    finally:
        os.close(descriptor)
    value = b"".join(chunks)
    if _stable_metadata(before) != _stable_metadata(after) or len(value) != before.st_size:
        raise HarnessError("INPUT_CHANGED_DURING_READ", f"{context} changed while being read")
    return value


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


def load_json_object_with_bytes(
    path: Path,
    context: str,
    *,
    confinement_root: Path | None = None,
) -> tuple[dict[str, object], bytes]:
    """Load and return the exact stable bytes used to parse one JSON object."""

    raw = read_file_bytes(path, context, confinement_root=confinement_root)
    try:
        text = raw.decode("utf-8")
        parsed = cast(object, json.loads(text))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError("JSON_INVALID", f"{context} is not valid JSON") from exc
    return expect_object(parsed, context), raw


def load_json_object(
    path: Path,
    context: str,
    *,
    confinement_root: Path | None = None,
) -> dict[str, object]:
    """Load UTF-8 JSON while normalizing parser failures."""

    value, _ = load_json_object_with_bytes(
        path,
        context,
        confinement_root=confinement_root,
    )
    return value


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


def write_new_file_bytes(
    path: Path,
    value: bytes,
    *,
    confinement_root: Path,
) -> None:
    """Create one evidence file exclusively beneath a symlink-free directory."""

    absolute_root, parts = _relative_beneath(path, confinement_root, "evidence artifact")
    directory_descriptor = _open_absolute_directory(absolute_root, "evidence artifact")
    descriptor: int | None = None
    try:
        for part in parts[:-1]:
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        descriptor = os.open(
            parts[-1],
            _WRITE_NEW_FLAGS,
            0o600,
            dir_fd=directory_descriptor,
        )
        view = memoryview(value)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    except OSError as exc:
        raise HarnessError(
            "ARTIFACT_WRITE_FAILED",
            "cannot write an evidence artifact",
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory_descriptor)


def write_new_canonical_json(path: Path, value: object, *, confinement_root: Path) -> None:
    """Create one canonical JSON artifact without overwriting an existing file."""

    write_new_file_bytes(
        path,
        canonical_json_bytes(value),
        confinement_root=confinement_root,
    )


def sha256_file(
    path: Path,
    deadline: float | None = None,
    *,
    confinement_root: Path | None = None,
) -> tuple[str, int]:
    """Hash a file incrementally and return digest plus byte count."""

    digest = hashlib.sha256()
    size = 0
    descriptor = _open_regular_file(path, "an input artifact", confinement_root)
    try:
        before = os.fstat(descriptor)
        while True:
            if deadline is not None and time.monotonic() > deadline:
                raise HarnessError("TIMEOUT_EXCEEDED", "candidate exceeded its timeout")
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
        after = os.fstat(descriptor)
    except OSError as exc:
        raise HarnessError("INPUT_READ_FAILED", "cannot read an input artifact") from exc
    finally:
        os.close(descriptor)
    if _stable_metadata(before) != _stable_metadata(after) or size != before.st_size:
        raise HarnessError(
            "INPUT_CHANGED_DURING_READ",
            "an input artifact changed while being read",
        )
    return digest.hexdigest(), size
