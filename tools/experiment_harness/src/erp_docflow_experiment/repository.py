"""Repository and path confinement rules for offline experiments."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

from erp_docflow_experiment.errors import HarnessError


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
    if resolved.exists():
        raise HarnessError("OUTPUT_ALREADY_EXISTS", "output bundle already exists")
    return resolved


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
