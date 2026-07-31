#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from fixturelib import (
    DATASET_ID,
    DATASET_VERSION,
    MAX_FILE_BYTES,
    MAX_PAGES,
    sha256_bytes,
    valid_cnpj,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIELD_NAMES = {
    "document_number",
    "issuer_name",
    "issuer_tax_id",
    "issued_on",
    "due_on",
    "total_amount",
    "currency",
}
FIELD_KEYS = {"raw_value", "normalized_value", "applicability", "evidence_refs"}
EVIDENCE_KEYS = {"artifact_ref", "page", "excerpt", "bbox", "coordinate_space"}
APPLICABILITIES = {"PRESENT", "NOT_APPLICABLE", "MISSING", "AMBIGUOUS"}
DOCUMENT_TYPES = {"INVOICE", "PAYMENT_SLIP", "RECEIPT", "OTHER"}
VALIDATION_REASON_CODES = {
    "REQUIRED_FIELD_MISSING",
    "VALIDATION_CONFLICT",
    "INVALID_TAX_ID",
    "INVALID_DATE",
    "INVALID_AMOUNT",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema_contract(profile_root: Path) -> list[str]:
    errors: list[str] = []
    schema = _load_json(profile_root / "extraction.schema.json")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("extraction schema must use JSON Schema Draft 2020-12")
    if set(schema.get("required", [])) != {
        "schema_id",
        "schema_version",
        "document_type",
        "fields",
    }:
        errors.append("extraction schema root requirements drifted")
    if schema.get("additionalProperties") is not False:
        errors.append("extraction schema root must reject additional properties")
    fields_schema = schema.get("properties", {}).get("fields", {})
    if set(fields_schema.get("required", [])) != FIELD_NAMES:
        errors.append("extraction schema field coverage drifted")
    if fields_schema.get("additionalProperties") is not False:
        errors.append("extraction schema fields must reject additional properties")
    base_field = schema.get("$defs", {}).get("baseField", {})
    if set(base_field.get("required", [])) != FIELD_KEYS:
        errors.append("extraction schema field envelope drifted")
    if base_field.get("additionalProperties") is not False:
        errors.append("extraction field envelope must reject additional properties")
    return errors


def _validate_field(
    fixture_id: str,
    name: str,
    value: Any,
    artifact_ref: str,
    page_count: int,
) -> list[str]:
    prefix = f"{fixture_id}: {name}"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{prefix} must be an object"]
    if set(value) != FIELD_KEYS:
        errors.append(f"{prefix} keys mismatch: {sorted(value)}")
    applicability = value.get("applicability")
    raw = value.get("raw_value")
    normalized = value.get("normalized_value")
    evidence_refs = value.get("evidence_refs")
    if applicability not in APPLICABILITIES:
        errors.append(f"{prefix} has invalid applicability")
    if not isinstance(evidence_refs, list):
        errors.append(f"{prefix} evidence_refs must be an array")
        evidence_refs = []
    if applicability == "PRESENT":
        if not isinstance(raw, str) or not raw:
            errors.append(f"{prefix} PRESENT requires non-empty raw_value")
        if not isinstance(normalized, str) or not normalized:
            errors.append(f"{prefix} PRESENT requires non-empty normalized_value")
        if not evidence_refs:
            errors.append(f"{prefix} PRESENT requires evidence")
    elif applicability in {"NOT_APPLICABLE", "MISSING"}:
        if raw is not None or normalized is not None or evidence_refs:
            errors.append(f"{prefix} {applicability} requires null values and no evidence")
    elif applicability == "AMBIGUOUS":
        if raw is not None and not isinstance(raw, str):
            errors.append(f"{prefix} AMBIGUOUS raw_value must be string or null")
        if normalized is not None:
            errors.append(f"{prefix} AMBIGUOUS normalized_value must be null")
        if not evidence_refs:
            errors.append(f"{prefix} AMBIGUOUS requires evidence")
    for index, evidence in enumerate(evidence_refs):
        evidence_prefix = f"{prefix} evidence[{index}]"
        if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_KEYS:
            errors.append(f"{evidence_prefix} keys mismatch")
            continue
        if evidence.get("artifact_ref") != artifact_ref:
            errors.append(f"{evidence_prefix} artifact_ref mismatch")
        page = evidence.get("page")
        if not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= page_count:
            errors.append(f"{evidence_prefix} page is outside the artifact")
        excerpt = evidence.get("excerpt")
        if not isinstance(excerpt, str) or not excerpt:
            errors.append(f"{evidence_prefix} excerpt must be non-empty")
        elif isinstance(raw, str) and raw not in excerpt:
            errors.append(f"{evidence_prefix} does not contain raw_value")
        if evidence.get("bbox") is not None or evidence.get("coordinate_space") is not None:
            errors.append(f"{evidence_prefix} bbox/coordinate_space must remain null in v1alpha")
    if normalized is not None:
        if name == "document_type" and normalized not in DOCUMENT_TYPES:
            errors.append(f"{prefix} has invalid document type")
        elif name == "issuer_tax_id" and re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", normalized) is None:
            errors.append(f"{prefix} has invalid normalized CNPJ shape")
        elif name in {"issued_on", "due_on"}:
            try:
                date.fromisoformat(normalized)
            except (TypeError, ValueError):
                errors.append(f"{prefix} is not a valid ISO date")
        elif name == "total_amount":
            try:
                parsed = Decimal(normalized)
            except (InvalidOperation, TypeError):
                errors.append(f"{prefix} is not a decimal")
            else:
                if parsed <= 0 or re.fullmatch(r"[0-9]+\.[0-9]{2}", normalized) is None:
                    errors.append(f"{prefix} must be a positive decimal with two places")
        elif name == "currency" and normalized != "BRL":
            errors.append(f"{prefix} currency must be BRL")
    return errors


def _validate_expected_output(
    fixture_id: str,
    output: Any,
    artifact_ref: str,
    page_count: int,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(output, dict):
        return [f"{fixture_id}: expected_output must be an object or null"]
    if set(output) != {"schema_id", "schema_version", "document_type", "fields"}:
        errors.append(f"{fixture_id}: expected_output root keys mismatch")
    if output.get("schema_id") != "payable_document":
        errors.append(f"{fixture_id}: expected_output schema_id mismatch")
    if output.get("schema_version") != DATASET_VERSION:
        errors.append(f"{fixture_id}: expected_output schema_version mismatch")
    errors.extend(
        _validate_field(
            fixture_id,
            "document_type",
            output.get("document_type"),
            artifact_ref,
            page_count,
        )
    )
    fields = output.get("fields")
    if not isinstance(fields, dict):
        errors.append(f"{fixture_id}: expected_output fields must be an object")
        return errors
    if set(fields) != FIELD_NAMES:
        errors.append(f"{fixture_id}: expected_output field coverage mismatch")
    for name in sorted(FIELD_NAMES & set(fields)):
        errors.extend(
            _validate_field(fixture_id, name, fields[name], artifact_ref, page_count)
        )
    return errors


def _business_validation_codes(output: dict[str, Any], rules: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    document_type = output["document_type"]["normalized_value"]
    fields = output["fields"]
    type_rules = rules["document_types"][document_type]
    failure_applicabilities = set(
        rules["applicability_policy"]["required_present_failure_applicabilities"]
    )
    for name in type_rules["required_present"]:
        if fields[name]["applicability"] in failure_applicabilities:
            codes.add("REQUIRED_FIELD_MISSING")
    allowed_not_applicable = set(type_rules["allowed_not_applicable"])
    for name, value in fields.items():
        if (
            value["applicability"] == "NOT_APPLICABLE"
            and name not in allowed_not_applicable
        ):
            codes.add("REQUIRED_FIELD_MISSING")
    for rule in rules["cross_field_rules"]:
        reason = rule["failure_reason_code"]
        if rule["id"] == "valid_iso_dates":
            for name in rule["fields"]:
                value = fields[name]
                if value["applicability"] != rule["when_applicability"]:
                    continue
                try:
                    date.fromisoformat(value["normalized_value"])
                except (TypeError, ValueError):
                    codes.add(reason)
        elif rule["id"] == "issued_on_not_after_due_on":
            values = [fields[name] for name in rule["when_present"]]
            if all(value["applicability"] == "PRESENT" for value in values):
                try:
                    if date.fromisoformat(values[0]["normalized_value"]) > date.fromisoformat(
                        values[1]["normalized_value"]
                    ):
                        codes.add(reason)
                except (TypeError, ValueError):
                    pass
        elif rule["id"] == "valid_cnpj_check_digits":
            tax_id = fields[rule["when_present"][0]]
            if tax_id["applicability"] == "PRESENT" and not valid_cnpj(
                str(tax_id["normalized_value"])
            ):
                codes.add(reason)
        elif rule["id"] == "positive_decimal_amount":
            amount = fields[rule["when_present"][0]]
            if amount["applicability"] == "AMBIGUOUS":
                codes.add(reason)
            elif amount["applicability"] == "PRESENT":
                try:
                    if Decimal(amount["normalized_value"]) <= 0:
                        codes.add(reason)
                except (InvalidOperation, TypeError):
                    codes.add(reason)
    return codes


def _select_fixtures(
    fixtures: list[dict[str, Any]],
    selector: dict[str, Any],
    output_fixture_ids: set[str],
) -> list[dict[str, Any]]:
    fixture_ids = set(selector.get("fixture_ids", []))
    splits = set(selector.get("splits", []))
    scenario_groups = set(selector.get("scenario_groups", []))
    excluded_groups = set(selector.get("exclude_scenario_groups", []))
    result: list[dict[str, Any]] = []
    for fixture in fixtures:
        if fixture_ids and fixture["id"] not in fixture_ids:
            continue
        if splits and fixture["split"] not in splits:
            continue
        if scenario_groups and fixture["scenario_group"] not in scenario_groups:
            continue
        if fixture["scenario_group"] in excluded_groups:
            continue
        if selector.get("requires_expected_output") and fixture["id"] not in output_fixture_ids:
            continue
        result.append(fixture)
    return result


def validate_dataset(target: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = target / "manifest.json"
    if not manifest_path.is_file():
        return [f"missing manifest: {manifest_path}"]
    manifest = _load_json(manifest_path)
    if manifest.get("dataset_id") != DATASET_ID or manifest.get("dataset_version") != DATASET_VERSION:
        errors.append("dataset identity/version mismatch")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 28:
        errors.append(f"expected 28 fixtures, got {len(fixtures) if isinstance(fixtures, list) else 'invalid'}")
        return errors

    profile_root = REPOSITORY_ROOT / "profiles" / DATASET_ID / DATASET_VERSION
    profile = _load_json(profile_root / "profile.json")
    reason_registry = set(_load_json(profile_root / "reason-codes.json")["reason_codes"])
    validation_rules = _load_json(profile_root / "validation-rules.json")
    errors.extend(_validate_schema_contract(profile_root))
    expected_rule_ids = {
        "valid_iso_dates",
        "issued_on_not_after_due_on",
        "valid_cnpj_check_digits",
        "positive_decimal_amount",
    }
    rule_ids = {rule.get("id") for rule in validation_rules.get("cross_field_rules", [])}
    if rule_ids != expected_rule_ids:
        errors.append(f"validation rule coverage mismatch: {sorted(rule_ids)}")
    for rule in validation_rules.get("cross_field_rules", []):
        if rule.get("failure_reason_code") not in reason_registry:
            errors.append(f"validation rule {rule.get('id')} has unknown reason code")
    if set(validation_rules.get("document_types", {})) != DOCUMENT_TYPES:
        errors.append("validation rule pack document type coverage mismatch")
    if profile.get("required_outputs") != {
        "text": True,
        "layout": False,
        "reading_order": False,
        "tables": False,
    }:
        errors.append("profile required_outputs drifted from v1alpha contract")
    outcomes = set(profile.get("native_text_assessment", {}).get("outcomes", []))
    recognize = next(
        (task for task in profile.get("task_graph", []) if task.get("id") == "recognize"),
        {},
    )
    if recognize.get("when_assessment") not in outcomes:
        errors.append("recognize task does not reference a registered assessment outcome")
    if profile.get("native_text_assessment", {}).get("thresholds") != "candidate_from_spike_82":
        errors.append("native-text assessment thresholds must be supplied by spike #82")

    ids: set[str] = set()
    family_splits: dict[str, set[str]] = defaultdict(set)
    family_split_counts: Counter[str] = Counter()
    scenario_counts: Counter[str] = Counter()
    seen_families: set[str] = set()
    tax_ids_by_split: dict[str, dict[str, int]] = defaultdict(
        lambda: {"numeric": 0, "alphanumeric": 0}
    )
    tax_id_splits: dict[str, set[str]] = defaultdict(set)
    tax_id_issuers: dict[str, set[str]] = defaultdict(set)
    fixtures_by_id = {fixture.get("id"): fixture for fixture in fixtures}
    expected_paths = {".gitattributes", "manifest.json"}
    output_fixture_ids: set[str] = set()

    for fixture in fixtures:
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or fixture_id in ids:
            errors.append(f"invalid or duplicate fixture id: {fixture_id}")
            continue
        ids.add(fixture_id)
        family_id = str(fixture.get("family_id"))
        split = str(fixture.get("split"))
        family_splits[family_id].add(split)
        if family_id not in seen_families:
            family_split_counts[split] += 1
            seen_families.add(family_id)
        scenario_counts[str(fixture.get("scenario_group"))] += 1
        reason_codes = fixture.get("expected", {}).get("reason_codes", [])
        unknown_codes = set(reason_codes) - reason_registry
        if unknown_codes:
            errors.append(f"{fixture_id}: unknown reason codes {sorted(unknown_codes)}")

        file_path = target / fixture["path"]
        truth_path = target / fixture["ground_truth"]
        expected_paths.update({fixture["path"], fixture["ground_truth"]})
        if not file_path.is_file():
            errors.append(f"{fixture_id}: missing file {fixture['path']}")
            continue
        payload = file_path.read_bytes()
        if fixture.get("sha256") != sha256_bytes(payload):
            errors.append(f"{fixture_id}: document sha256 mismatch")
        if fixture.get("size_bytes") != len(payload):
            errors.append(f"{fixture_id}: document size mismatch")
        if not truth_path.is_file():
            errors.append(f"{fixture_id}: missing ground truth")
            continue
        truth_payload = truth_path.read_bytes()
        if fixture.get("ground_truth_sha256") != sha256_bytes(truth_payload):
            errors.append(f"{fixture_id}: ground truth sha256 mismatch")
        if fixture.get("ground_truth_size_bytes") != len(truth_payload):
            errors.append(f"{fixture_id}: ground truth size mismatch")
        truth = json.loads(truth_payload)
        if truth.get("fixture_id") != fixture_id or truth.get("ground_truth_version") != DATASET_VERSION:
            errors.append(f"{fixture_id}: ground truth identity/version mismatch")
        if truth.get("page_count") != fixture.get("page_count"):
            errors.append(f"{fixture_id}: ground truth page count mismatch")
        if truth.get("expected_failure_stage") != fixture.get("expected", {}).get("failure_stage"):
            errors.append(f"{fixture_id}: failure stage mismatch")
        classification = truth.get("classification")
        if classification is not None and classification.get("label") != fixture.get("document_type"):
            errors.append(f"{fixture_id}: classification label mismatch")

        output = truth.get("expected_output")
        quarantined = fixture.get("expected", {}).get("routing") == "QUARANTINE_INPUT"
        if quarantined and output is not None:
            errors.append(f"{fixture_id}: quarantined fixture must not have expected_output")
        if not quarantined and output is None:
            errors.append(f"{fixture_id}: reviewable fixture requires expected_output")
        if output is not None:
            output_fixture_ids.add(fixture_id)
            structural_errors = _validate_expected_output(
                fixture_id,
                output,
                fixture["path"],
                fixture["page_count"],
            )
            errors.extend(structural_errors)
            if not structural_errors:
                actual_validation_codes = _business_validation_codes(
                    output, validation_rules
                )
                expected_validation_codes = set(reason_codes) & VALIDATION_REASON_CODES
                if actual_validation_codes != expected_validation_codes:
                    errors.append(
                        f"{fixture_id}: business validation codes mismatch; "
                        f"expected {sorted(expected_validation_codes)}, "
                        f"got {sorted(actual_validation_codes)}"
                    )
                tax_field = output["fields"]["issuer_tax_id"]
                expected_invalid = "INVALID_TAX_ID" in reason_codes
                if tax_field["applicability"] == "PRESENT" and not expected_invalid:
                    normalized = str(tax_field["normalized_value"])
                    kind = "numeric" if normalized.isdigit() else "alphanumeric"
                    tax_ids_by_split[split][kind] += 1
                    tax_id_splits[normalized].add(split)
                    issuer = str(output["fields"]["issuer_name"]["normalized_value"])
                    tax_id_issuers[normalized].add(issuer)

    actual_paths = {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file()
    }
    for extra in sorted(actual_paths - expected_paths):
        errors.append(f"unexpected dataset artifact: {extra}")
    for family, splits in sorted(family_splits.items()):
        if len(splits) != 1:
            errors.append(f"split leakage for family {family}: {sorted(splits)}")
    if len(family_splits) != 20:
        errors.append(f"expected 20 families, got {len(family_splits)}")
    if family_split_counts != Counter({"development": 12, "validation": 4, "test": 4}):
        errors.append(f"family split counts mismatch: {dict(family_split_counts)}")
    expected_scenarios = Counter(
        {"BORN_DIGITAL": 6, "SCAN": 6, "IMAGE": 4, "HYBRID": 2, "FAILURE_LIMIT": 10}
    )
    if scenario_counts != expected_scenarios:
        errors.append(f"scenario group counts mismatch: {dict(scenario_counts)}")
    if not any(
        fixture.get("split") == "test" and fixture.get("scenario_group") == "FAILURE_LIMIT"
        for fixture in fixtures
    ):
        errors.append("test split has no held-out failure/limit scenario")
    for split in ("development", "validation", "test"):
        for kind in ("numeric", "alphanumeric"):
            if tax_ids_by_split[split][kind] == 0:
                errors.append(f"{split}: missing valid {kind} CNPJ")
    for tax_id, splits in sorted(tax_id_splits.items()):
        if len(splits) != 1:
            errors.append(f"CNPJ split leakage for {tax_id}: {sorted(splits)}")
        if len(tax_id_issuers[tax_id]) != 1:
            errors.append(f"CNPJ assigned to multiple issuers: {tax_id}")

    acceptance = _load_json(
        REPOSITORY_ROOT
        / "benchmarks"
        / DATASET_ID
        / DATASET_VERSION
        / "acceptance.json"
    )
    protocol = acceptance.get("evaluation_protocol", {})
    required_protocols = {
        "integrity",
        "born_digital_required_field_recoverability",
        "classification_macro_f1",
        "clean_ocr",
        "degraded_ocr",
        "failure_reason_codes",
        "review_routing",
        "auto_accept",
        "latency_and_memory",
    }
    if set(protocol) != required_protocols:
        errors.append(f"acceptance protocol coverage mismatch: {sorted(protocol)}")
    selected = {
        name: _select_fixtures(fixtures, specification.get("selector", {}), output_fixture_ids)
        for name, specification in protocol.items()
        if "selector" in specification
    }
    if len(selected.get("integrity", [])) != 28:
        errors.append("integrity metric selector must cover all 28 fixtures")
    if len(selected.get("born_digital_required_field_recoverability", [])) != 6:
        errors.append("born-digital recoverability selector must cover six baseline fixtures")
    classification = selected.get("classification_macro_f1", [])
    classification_families = {fixture["family_id"] for fixture in classification}
    classification_policy = protocol.get("classification_macro_f1", {})
    if (
        len(classification_families)
        < classification_policy.get("minimum_families_for_conclusive_result", 0)
        and classification_policy.get("below_minimum_result") != "INCONCLUSIVE"
    ):
        errors.append("small classification sample must produce INCONCLUSIVE")
    for metric in ("clean_ocr", "degraded_ocr"):
        pages = sum(fixture["page_count"] for fixture in selected.get(metric, []))
        if pages < protocol.get(metric, {}).get("minimum_pages", 0):
            errors.append(f"{metric} selector does not meet its declared minimum_pages")
    if len(selected.get("failure_reason_codes", [])) != 10:
        errors.append("failure reason-code metric selector must cover ten fixtures")
    review_selected = selected.get("review_routing", [])
    if not review_selected or any(
        fixture["expected"]["routing"] != "OPEN_REVIEW"
        for fixture in review_selected
    ):
        errors.append("review routing selector/outcomes mismatch")
    if any(
        fixture["expected"]["routing"] == "AUTO_ACCEPT"
        for fixture in selected.get("auto_accept", [])
    ):
        errors.append("v1alpha acceptance set must not contain auto-accept routing")

    duplicate = fixtures_by_id.get("dev-inv001-duplicate")
    source = fixtures_by_id.get("dev-inv001-native")
    if not duplicate or not source or not (
        duplicate.get("duplicate_of") == source.get("id")
        and duplicate.get("sha256") == source.get("sha256")
        and duplicate.get("scenario_group") == "FAILURE_LIMIT"
        and "DUPLICATE_CONTENT" in duplicate.get("expected", {}).get("reason_codes", [])
    ):
        errors.append("duplicate fixture does not preserve source identity/hash/outcome")
    resource = fixtures_by_id.get("val-resource-limit")
    if not resource or not (
        resource.get("size_bytes", 0) > MAX_FILE_BYTES
        and resource.get("page_count", 0) > MAX_PAGES
    ):
        errors.append("resource-limit fixture does not exceed both approved limits")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a generated document fixture dataset")
    parser.add_argument("--dataset", default=f"{DATASET_ID}/{DATASET_VERSION}")
    arguments = parser.parse_args()
    target = REPOSITORY_ROOT / "datasets" / arguments.dataset
    errors = validate_dataset(target)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"dataset is valid: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
