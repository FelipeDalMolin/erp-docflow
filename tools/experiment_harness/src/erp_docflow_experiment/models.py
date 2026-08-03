"""Validated input models for an experiment run."""

from __future__ import annotations

import re
from dataclasses import dataclass

from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.jsonio import (
    expect_bool,
    expect_int,
    expect_list,
    expect_object,
    expect_string,
    reject_unknown_keys,
    require_keys,
)

IDENTIFIER_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{2,127}")
REPOSITORY_PATH_PATTERN = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")
FIXTURE_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,127}")
ALLOWED_SPLITS = frozenset({"development", "validation", "test"})


@dataclass(frozen=True)
class CandidateSpec:
    """A registry key and JSON configuration for one candidate."""

    candidate_id: str
    configuration: dict[str, object]


@dataclass(frozen=True)
class Controls:
    """Fail-closed execution controls supplied by the manifest."""

    runtime_egress_allowed: bool
    real_data_allowed: bool
    max_parallel_jobs: int
    timeout_seconds: int
    random_seed: int


@dataclass(frozen=True)
class FixtureSelector:
    """A deterministic subset of the dataset manifest."""

    splits: tuple[str, ...]
    fixture_ids: tuple[str, ...]
    expected_fixture_count: int


@dataclass(frozen=True)
class ExperimentManifest:
    """Strict v1alpha experiment manifest."""

    schema_version: str
    experiment_id: str
    issue: int
    purpose: str
    capability: str
    profile_ref: str
    dataset_manifest_ref: str
    acceptance_policy_ref: str
    dependency_lock_ref: str
    dataset_classification: str
    candidate: CandidateSpec
    controls: Controls
    selector: FixtureSelector


def _parse_string_list(value: object, context: str) -> tuple[str, ...]:
    items = expect_list(value, context)
    parsed = tuple(expect_string(item, f"{context}[]") for item in items)
    if len(set(parsed)) != len(parsed):
        raise HarnessError("SCHEMA_INVALID", f"{context} contains duplicate values")
    return parsed


def _bounded_string(value: object, context: str, maximum: int) -> str:
    parsed = expect_string(value, context)
    if len(parsed) > maximum:
        raise HarnessError("SCHEMA_INVALID", f"{context} exceeds its maximum length")
    return parsed


def _repository_reference(value: object, context: str) -> str:
    parsed = _bounded_string(value, context, 512)
    if REPOSITORY_PATH_PATTERN.fullmatch(parsed) is None or ".." in parsed.split("/"):
        raise HarnessError("PATH_NOT_ALLOWED", f"{context} is not a repository path")
    return parsed


def parse_manifest(value: dict[str, object]) -> ExperimentManifest:
    """Parse and validate the manifest contract without external schema libraries."""

    allowed = {
        "schema_version",
        "experiment_id",
        "issue",
        "purpose",
        "capability",
        "profile_ref",
        "dataset_manifest_ref",
        "acceptance_policy_ref",
        "dependency_lock_ref",
        "dataset_classification",
        "candidate",
        "controls",
        "fixture_selector",
    }
    require_keys(value, allowed, "experiment manifest")
    reject_unknown_keys(value, allowed, "experiment manifest")

    schema_version = expect_string(value["schema_version"], "schema_version")
    if schema_version != "experiment-manifest/v1alpha":
        raise HarnessError("SCHEMA_VERSION_UNSUPPORTED", "unsupported experiment schema")

    issue = expect_int(value["issue"], "issue")
    if issue <= 0:
        raise HarnessError("SCHEMA_INVALID", "issue must be positive")

    classification = expect_string(value["dataset_classification"], "dataset_classification")
    if classification != "synthetic":
        raise HarnessError("REAL_DATA_NOT_ALLOWED", "only synthetic datasets are allowed")

    candidate_value = expect_object(value["candidate"], "candidate")
    candidate_keys = {"id", "configuration"}
    require_keys(candidate_value, candidate_keys, "candidate")
    reject_unknown_keys(candidate_value, candidate_keys, "candidate")
    configuration = expect_object(candidate_value["configuration"], "candidate.configuration")
    candidate = CandidateSpec(
        candidate_id=expect_string(candidate_value["id"], "candidate.id"),
        configuration=configuration,
    )

    controls_value = expect_object(value["controls"], "controls")
    controls_keys = {
        "runtime_egress_allowed",
        "real_data_allowed",
        "max_parallel_jobs",
        "timeout_seconds",
        "random_seed",
    }
    require_keys(controls_value, controls_keys, "controls")
    reject_unknown_keys(controls_value, controls_keys, "controls")
    controls = Controls(
        runtime_egress_allowed=expect_bool(
            controls_value["runtime_egress_allowed"], "controls.runtime_egress_allowed"
        ),
        real_data_allowed=expect_bool(
            controls_value["real_data_allowed"], "controls.real_data_allowed"
        ),
        max_parallel_jobs=expect_int(
            controls_value["max_parallel_jobs"], "controls.max_parallel_jobs"
        ),
        timeout_seconds=expect_int(
            controls_value["timeout_seconds"], "controls.timeout_seconds"
        ),
        random_seed=expect_int(controls_value["random_seed"], "controls.random_seed"),
    )
    if controls.runtime_egress_allowed:
        raise HarnessError("EGRESS_NOT_ALLOWED", "runtime egress must remain disabled")
    if controls.real_data_allowed:
        raise HarnessError("REAL_DATA_NOT_ALLOWED", "real data must remain disabled")
    if controls.max_parallel_jobs != 1:
        raise HarnessError("CONCURRENCY_NOT_ALLOWED", "max_parallel_jobs must equal 1")
    if controls.timeout_seconds <= 0:
        raise HarnessError("SCHEMA_INVALID", "timeout_seconds must be positive")
    if controls.timeout_seconds > 86400:
        raise HarnessError("SCHEMA_INVALID", "timeout_seconds exceeds the allowed maximum")
    if controls.random_seed < 0 or controls.random_seed > 4294967295:
        raise HarnessError("SCHEMA_INVALID", "random_seed is outside the allowed range")

    selector_value = expect_object(value["fixture_selector"], "fixture_selector")
    selector_keys = {"splits", "fixture_ids", "expected_fixture_count"}
    require_keys(selector_value, selector_keys, "fixture_selector")
    reject_unknown_keys(selector_value, selector_keys, "fixture_selector")
    splits = _parse_string_list(selector_value["splits"], "fixture_selector.splits")
    fixture_ids = _parse_string_list(
        selector_value["fixture_ids"], "fixture_selector.fixture_ids"
    )
    expected_count = expect_int(
        selector_value["expected_fixture_count"], "fixture_selector.expected_fixture_count"
    )
    if not splits or len(splits) > 3 or not set(splits).issubset(ALLOWED_SPLITS):
        raise HarnessError("SCHEMA_INVALID", "fixture selector contains invalid splits")
    if expected_count <= 0:
        raise HarnessError("SCHEMA_INVALID", "fixture selector must select at least one fixture")
    if any(FIXTURE_ID_PATTERN.fullmatch(fixture_id) is None for fixture_id in fixture_ids):
        raise HarnessError("SCHEMA_INVALID", "fixture selector contains an invalid fixture ID")

    experiment_id = expect_string(value["experiment_id"], "experiment_id")
    if IDENTIFIER_PATTERN.fullmatch(experiment_id) is None:
        raise HarnessError("SCHEMA_INVALID", "experiment_id has an invalid format")

    return ExperimentManifest(
        schema_version=schema_version,
        experiment_id=experiment_id,
        issue=issue,
        purpose=_bounded_string(value["purpose"], "purpose", 1000),
        capability=_bounded_string(value["capability"], "capability", 128),
        profile_ref=_repository_reference(value["profile_ref"], "profile_ref"),
        dataset_manifest_ref=_repository_reference(
            value["dataset_manifest_ref"], "dataset_manifest_ref"
        ),
        acceptance_policy_ref=_repository_reference(
            value["acceptance_policy_ref"], "acceptance_policy_ref"
        ),
        dependency_lock_ref=_repository_reference(
            value["dependency_lock_ref"], "dependency_lock_ref"
        ),
        dataset_classification=classification,
        candidate=candidate,
        controls=controls,
        selector=FixtureSelector(
            splits=splits,
            fixture_ids=fixture_ids,
            expected_fixture_count=expected_count,
        ),
    )
