"""Manifest preparation against repository-owned inputs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import (
    canonical_json_bytes,
    expect_bool,
    expect_list,
    expect_object,
    expect_string,
    load_json_object_with_bytes,
    read_file_bytes,
)
from erp_docflow_experiment.models import ExperimentManifest, parse_manifest
from erp_docflow_experiment.repository import resolve_repo_file

CANDIDATE_DEPENDENCY_LOCKS = {
    "integrity_probe/v1": "tools/experiment_harness/uv.lock",
}
KNOWN_CANDIDATES = frozenset(CANDIDATE_DEPENDENCY_LOCKS)


@dataclass(frozen=True)
class PreparedExperiment:
    """A manifest whose references and selected fixtures have been verified."""

    manifest: ExperimentManifest
    manifest_value: dict[str, object]
    manifest_path: Path
    profile_path: Path
    dataset_manifest_path: Path
    dataset_manifest_value: dict[str, object]
    acceptance_policy_path: Path
    dependency_lock_path: Path
    selected_fixtures: tuple[dict[str, object], ...]
    input_digests: dict[str, str]


def _select_fixtures(
    manifest: ExperimentManifest,
    dataset_value: dict[str, object],
) -> tuple[dict[str, object], ...]:
    fixtures = expect_list(dataset_value.get("fixtures"), "dataset manifest fixtures")
    requested_ids = set(manifest.selector.fixture_ids)
    requested_splits = set(manifest.selector.splits)
    selected: list[dict[str, object]] = []
    all_ids: set[str] = set()

    for index, item in enumerate(fixtures):
        fixture = expect_object(item, f"dataset fixture {index}")
        fixture_id = expect_string(fixture.get("id"), f"dataset fixture {index}.id")
        split = expect_string(fixture.get("split"), f"dataset fixture {fixture_id}.split")
        if fixture_id in all_ids:
            raise HarnessError("DATASET_INVALID", "dataset contains duplicate fixture IDs")
        all_ids.add(fixture_id)
        if split in requested_splits and (not requested_ids or fixture_id in requested_ids):
            selected.append(fixture)

    missing_ids = requested_ids - all_ids
    if missing_ids:
        raise HarnessError(
            "FIXTURE_NOT_FOUND",
            f"fixture selector references {len(missing_ids)} unknown fixture IDs",
        )
    selected.sort(key=lambda fixture: expect_string(fixture.get("id"), "fixture.id"))
    if len(selected) != manifest.selector.expected_fixture_count:
        raise HarnessError(
            "FIXTURE_COUNT_MISMATCH",
            "selected fixture count differs from expected_fixture_count",
        )
    return tuple(selected)


def prepare_experiment(repo_root: Path, manifest_path: Path) -> PreparedExperiment:
    """Load a v1alpha manifest, enforce controls and resolve all static inputs."""

    resolved_manifest = manifest_path.resolve()
    try:
        resolved_manifest.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise HarnessError("PATH_NOT_ALLOWED", "manifest must be inside the repository") from exc
    if not resolved_manifest.is_file():
        raise HarnessError("INPUT_NOT_FOUND", "experiment manifest does not exist")

    manifest_value, manifest_bytes = load_json_object_with_bytes(
        resolved_manifest,
        "experiment manifest",
        confinement_root=repo_root,
    )
    manifest = parse_manifest(manifest_value)
    if manifest.candidate.candidate_id not in KNOWN_CANDIDATES:
        raise HarnessError("CANDIDATE_NOT_REGISTERED", "candidate is not in the closed registry")
    if manifest.dependency_lock_ref != CANDIDATE_DEPENDENCY_LOCKS[
        manifest.candidate.candidate_id
    ]:
        raise HarnessError(
            "DEPENDENCY_LOCK_MISMATCH",
            "candidate must use its registered dependency lock",
        )
    if manifest.candidate.candidate_id == "integrity_probe/v1":
        if manifest.capability != "harness_integrity":
            raise HarnessError(
                "CAPABILITY_MISMATCH",
                "integrity_probe/v1 is limited to harness_integrity",
            )
        configuration = manifest.candidate.configuration
        if set(configuration) != {"verify_ground_truth"} or not expect_bool(
            configuration.get("verify_ground_truth"),
            "candidate.configuration.verify_ground_truth",
        ):
            raise HarnessError(
                "CANDIDATE_CONFIGURATION_INVALID",
                "integrity_probe/v1 requires verify_ground_truth=true",
            )

    profile_path = resolve_repo_file(repo_root, manifest.profile_ref, "profile_ref")
    dataset_path = resolve_repo_file(
        repo_root,
        manifest.dataset_manifest_ref,
        "dataset_manifest_ref",
    )
    acceptance_path = resolve_repo_file(
        repo_root,
        manifest.acceptance_policy_ref,
        "acceptance_policy_ref",
    )
    lock_path = resolve_repo_file(repo_root, manifest.dependency_lock_ref, "dependency_lock_ref")

    profile_value, profile_bytes = load_json_object_with_bytes(
        profile_path,
        "profile",
        confinement_root=repo_root,
    )
    if expect_string(profile_value.get("data_classification"), "profile.data_classification") != (
        manifest.dataset_classification
    ):
        raise HarnessError("DATA_CLASSIFICATION_MISMATCH", "profile classification differs")
    profile_benchmark = expect_object(profile_value.get("benchmark"), "profile.benchmark")
    if (
        expect_string(
            profile_benchmark.get("dataset_manifest"),
            "profile.benchmark.dataset_manifest",
        )
        != manifest.dataset_manifest_ref
        or expect_string(
            profile_benchmark.get("acceptance_policy"),
            "profile.benchmark.acceptance_policy",
        )
        != manifest.acceptance_policy_ref
    ):
        raise HarnessError("INPUT_REFERENCE_MISMATCH", "profile references another benchmark")

    dataset_value, dataset_bytes = load_json_object_with_bytes(
        dataset_path,
        "dataset manifest",
        confinement_root=repo_root,
    )
    if expect_string(dataset_value.get("classification"), "dataset.classification") != (
        manifest.dataset_classification
    ):
        raise HarnessError("DATA_CLASSIFICATION_MISMATCH", "dataset classification differs")
    if expect_string(dataset_value.get("profile_ref"), "dataset.profile_ref") != (
        manifest.profile_ref
    ):
        raise HarnessError("INPUT_REFERENCE_MISMATCH", "dataset references another profile")

    acceptance_value, acceptance_bytes = load_json_object_with_bytes(
        acceptance_path,
        "acceptance policy",
        confinement_root=repo_root,
    )
    policy_dataset = expect_string(
        acceptance_value.get("dataset_manifest"),
        "acceptance_policy.dataset_manifest",
    )
    if policy_dataset != manifest.dataset_manifest_ref:
        raise HarnessError(
            "INPUT_REFERENCE_MISMATCH",
            "acceptance policy references another dataset",
        )

    selected_fixtures = _select_fixtures(manifest, dataset_value)
    lock_bytes = read_file_bytes(
        lock_path,
        "dependency lock",
        confinement_root=repo_root,
    )
    input_bytes = {
        "experiment_manifest": manifest_bytes,
        "profile": profile_bytes,
        "dataset_manifest": dataset_bytes,
        "acceptance_policy": acceptance_bytes,
        "dependency_lock": lock_bytes,
    }
    digests = {
        name: hashlib.sha256(value).hexdigest()
        for name, value in sorted(input_bytes.items())
    }
    digests["candidate_configuration"] = hashlib.sha256(
        canonical_json_bytes(manifest.candidate.configuration)
    ).hexdigest()

    return PreparedExperiment(
        manifest=manifest,
        manifest_value=manifest_value,
        manifest_path=resolved_manifest,
        profile_path=profile_path,
        dataset_manifest_path=dataset_path,
        dataset_manifest_value=dataset_value,
        acceptance_policy_path=acceptance_path,
        dependency_lock_path=lock_path,
        selected_fixtures=selected_fixtures,
        input_digests=digests,
    )
