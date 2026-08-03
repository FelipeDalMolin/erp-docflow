"""Repository and path confinement rules for offline experiments."""

from __future__ import annotations

import ctypes
import errno
import os
import re
import secrets
import stat
from pathlib import Path, PurePosixPath

from erp_docflow_experiment.errors import HarnessError

_DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_OUTPUT_COMPONENT_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_RENAME_NOREPLACE = 1


def find_repo_root(start: Path) -> Path:
    """Locate the Git worktree root without invoking user-controlled commands."""

    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    raise HarnessError("REPOSITORY_NOT_FOUND", "run the harness inside the repository")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _contains_symlink(path: Path, root: Path) -> bool:
    """Detect symlinks in an existing lexical path without dereferencing them first."""

    lexical_path = Path(os.path.abspath(path))
    lexical_root = Path(os.path.abspath(root))
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError:
        return False
    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            return True
    return False


def _open_absolute_directory(path: Path, reason_code: str) -> int:
    """Open an absolute directory path component-by-component without symlinks."""

    absolute = Path(os.path.abspath(path))
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
        raise HarnessError(reason_code, "directory path contains an unsafe component") from exc
    assert descriptor is not None
    return descriptor


def _directory_identity(descriptor: int) -> tuple[int, int]:
    metadata = os.fstat(descriptor)
    if not stat.S_ISDIR(metadata.st_mode):
        raise HarnessError("OUTPUT_PATH_NOT_ALLOWED", "output path is not a directory")
    return metadata.st_dev, metadata.st_ino


def _rename_noreplace(parent_descriptor: int, source: str, destination: str) -> None:
    """Atomically publish a Linux directory without replacing an existing destination."""

    library = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = library.renameat2
    except AttributeError as exc:
        raise HarnessError(
            "OUTPUT_PUBLISH_UNSUPPORTED",
            "atomic no-replace publication is unavailable",
        ) from exc
    renameat2.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    renameat2.restype = ctypes.c_int
    result = renameat2(
        parent_descriptor,
        os.fsencode(source),
        parent_descriptor,
        os.fsencode(destination),
        _RENAME_NOREPLACE,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
        raise HarnessError("OUTPUT_ALREADY_EXISTS", "output bundle already exists")
    raise HarnessError(
        "OUTPUT_PUBLISH_FAILED",
        "cannot publish the completed evidence bundle",
    ) from OSError(error_number, os.strerror(error_number))


def resolve_repo_file(repo_root: Path, reference: str, context: str) -> Path:
    """Resolve a repository-relative regular file and reject traversal/symlinks outside it."""

    relative = PurePosixPath(reference)
    if relative.is_absolute() or ".." in relative.parts or reference != relative.as_posix():
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} must be repository-relative")
    resolved = (repo_root / Path(*relative.parts)).resolve()
    if not _inside(resolved, repo_root):
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} leaves the repository")
    if not resolved.is_file():
        raise HarnessError("INPUT_NOT_FOUND", f"{context} does not reference a regular file")
    return resolved


def resolve_dataset_file(
    repo_root: Path,
    dataset_directory: Path,
    reference: str,
    context: str,
) -> Path:
    """Resolve a dataset-local file while retaining repository confinement."""

    relative = PurePosixPath(reference)
    if relative.is_absolute() or ".." in relative.parts or reference != relative.as_posix():
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} must be dataset-relative")
    resolved = (dataset_directory / Path(*relative.parts)).resolve()
    if not _inside(resolved, repo_root) or not _inside(resolved, dataset_directory.resolve()):
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} leaves the dataset directory")
    if not resolved.is_file():
        raise HarnessError("INPUT_NOT_FOUND", f"{context} does not reference a regular file")
    return resolved


def resolve_output_directory(repo_root: Path, requested: Path) -> Path:
    """Allow new bundles only below the repository's ignored evidence root."""

    resolved_repo = repo_root.resolve()
    requested_path = resolved_repo / requested if not requested.is_absolute() else requested
    if _contains_symlink(requested_path, resolved_repo):
        raise HarnessError(
            "OUTPUT_PATH_NOT_ALLOWED",
            "output path cannot contain symlinks",
        )
    resolved = (
        requested_path.resolve()
    )
    artifacts_root = resolved_repo / ".artifacts"
    evidence_path = artifacts_root / "experiments"
    if artifacts_root.is_symlink() or evidence_path.is_symlink():
        raise HarnessError(
            "OUTPUT_PATH_NOT_ALLOWED",
            "evidence root cannot be a symlink",
        )
    evidence_root = evidence_path.resolve()
    if not _inside(evidence_root, resolved_repo):
        raise HarnessError(
            "OUTPUT_PATH_NOT_ALLOWED",
            "evidence root leaves the repository",
        )
    if resolved == evidence_root or not _inside(resolved, evidence_root):
        raise HarnessError(
            "OUTPUT_PATH_NOT_ALLOWED",
            "output must be a child of .artifacts/experiments",
        )
    output_relative = resolved.relative_to(evidence_root)
    if any(
        _OUTPUT_COMPONENT_PATTERN.fullmatch(part) is None
        for part in output_relative.parts
    ):
        raise HarnessError(
            "OUTPUT_PATH_NOT_ALLOWED",
            "output path contains an unsupported component",
        )
    if resolved.exists():
        raise HarnessError("OUTPUT_ALREADY_EXISTS", "output bundle already exists")
    return resolved


def create_staging_directory(
    repo_root: Path,
    output: Path,
) -> tuple[Path, tuple[int, int]]:
    """Create a private sibling staging directory through held directory descriptors."""

    resolved_repo = repo_root.resolve()
    resolved_output = output.absolute()
    try:
        parent_relative = resolved_output.parent.relative_to(resolved_repo)
    except ValueError as exc:
        raise HarnessError("OUTPUT_PATH_NOT_ALLOWED", "output leaves the repository") from exc

    parent_descriptor = _open_absolute_directory(resolved_repo, "OUTPUT_PATH_NOT_ALLOWED")
    try:
        for part in parent_relative.parts:
            try:
                os.mkdir(part, 0o700, dir_fd=parent_descriptor)
            except FileExistsError:
                pass
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=parent_descriptor)
            os.close(parent_descriptor)
            parent_descriptor = next_descriptor

        try:
            os.stat(resolved_output.name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise HarnessError("OUTPUT_ALREADY_EXISTS", "output bundle already exists")

        for _ in range(32):
            staging_name = f".erp-docflow-staging-{secrets.token_hex(8)}"
            try:
                os.mkdir(staging_name, 0o700, dir_fd=parent_descriptor)
            except FileExistsError:
                continue
            staging_descriptor = os.open(
                staging_name,
                _DIRECTORY_FLAGS,
                dir_fd=parent_descriptor,
            )
            try:
                identity = _directory_identity(staging_descriptor)
            finally:
                os.close(staging_descriptor)
            return resolved_output.parent / staging_name, identity
    except OSError as exc:
        raise HarnessError("OUTPUT_CREATE_FAILED", "cannot create output staging") from exc
    finally:
        os.close(parent_descriptor)
    raise HarnessError("OUTPUT_CREATE_FAILED", "cannot allocate a unique output staging")


def assert_directory_identity(path: Path, expected: tuple[int, int]) -> None:
    """Fail when a staging path no longer names the directory that was created."""

    descriptor = _open_absolute_directory(path, "OUTPUT_PATH_NOT_ALLOWED")
    try:
        actual = _directory_identity(descriptor)
    finally:
        os.close(descriptor)
    if actual != expected:
        raise HarnessError("OUTPUT_PATH_CHANGED", "output staging identity changed")


def publish_staging_directory(
    staging: Path,
    expected_identity: tuple[int, int],
    output: Path,
) -> None:
    """Atomically rename completed staging to its final path without replacement."""

    if staging.parent != output.parent:
        raise HarnessError("OUTPUT_PATH_NOT_ALLOWED", "staging and output must be siblings")
    parent_descriptor = _open_absolute_directory(output.parent, "OUTPUT_PATH_NOT_ALLOWED")
    try:
        try:
            metadata = os.stat(staging.name, dir_fd=parent_descriptor, follow_symlinks=False)
        except OSError as exc:
            raise HarnessError("OUTPUT_PATH_CHANGED", "output staging disappeared") from exc
        if not stat.S_ISDIR(metadata.st_mode) or (metadata.st_dev, metadata.st_ino) != (
            expected_identity
        ):
            raise HarnessError("OUTPUT_PATH_CHANGED", "output staging identity changed")
        _rename_noreplace(parent_descriptor, staging.name, output.name)
        published = os.stat(output.name, dir_fd=parent_descriptor, follow_symlinks=False)
        if not stat.S_ISDIR(published.st_mode) or (published.st_dev, published.st_ino) != (
            expected_identity
        ):
            raise HarnessError("OUTPUT_PATH_CHANGED", "published output identity changed")
    finally:
        os.close(parent_descriptor)


def resolve_existing_bundle(repo_root: Path, requested: Path) -> Path:
    """Resolve an existing bundle below the local experiment evidence root."""

    resolved_repo = repo_root.resolve()
    requested_path = resolved_repo / requested if not requested.is_absolute() else requested
    if _contains_symlink(requested_path, resolved_repo):
        raise HarnessError("BUNDLE_NOT_FOUND", "bundle directory cannot be a symlink")
    resolved = (
        requested_path.resolve()
    )
    artifacts_root = resolved_repo / ".artifacts"
    evidence_path = artifacts_root / "experiments"
    if artifacts_root.is_symlink() or evidence_path.is_symlink():
        raise HarnessError("BUNDLE_NOT_FOUND", "evidence root cannot be a symlink")
    evidence_root = evidence_path.resolve()
    if (
        not _inside(evidence_root, resolved_repo)
        or resolved == evidence_root
        or not _inside(resolved, evidence_root)
        or not resolved.is_dir()
    ):
        raise HarnessError(
            "BUNDLE_NOT_FOUND",
            "bundle must be an existing directory below .artifacts/experiments",
        )
    return resolved


def repo_relative(repo_root: Path, path: Path) -> str:
    """Return a stable POSIX repository-relative path."""

    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise HarnessError("PATH_NOT_ALLOWED", "path leaves the repository") from exc


def safe_bundle_member(bundle_root: Path, member: str) -> Path:
    """Resolve one bundle inventory member without traversal."""

    relative = PurePosixPath(member)
    if (
        relative.is_absolute()
        or not relative.parts
        or ".." in relative.parts
        or member != relative.as_posix()
    ):
        raise HarnessError("ARTIFACT_PATH_INVALID", "bundle contains an unsafe artifact path")
    resolved = (bundle_root / Path(*relative.parts)).resolve()
    if not _inside(resolved, bundle_root.resolve()):
        raise HarnessError("ARTIFACT_PATH_INVALID", "artifact leaves the bundle")
    return resolved
