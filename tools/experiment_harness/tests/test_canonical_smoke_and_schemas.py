"""Acceptance tests for repository-owned schemas and all 28 canonical fixtures."""

from __future__ import annotations

import json
import time
from pathlib import Path

from erp_docflow_experiment.candidates import run_integrity_probe
from erp_docflow_experiment.jsonio import canonical_json_bytes
from erp_docflow_experiment.manifest import prepare_experiment
from erp_docflow_experiment.repository import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
SCHEMA_ROOT = REPO_ROOT / "experiments" / "schemas" / "v1alpha"
SMOKE_MANIFEST = (
    REPO_ROOT / "experiments" / "payable_document_pt_br" / "v1alpha" / "harness-smoke.json"
)


def _json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_all_versioned_contract_schemas_are_closed_and_identifiable() -> None:
    expected = {
        "artifact-bundle.schema.json": "artifact-bundle/v1alpha",
        "benchmark-run.schema.json": "benchmark-run/v1alpha",
        "experiment-manifest.schema.json": "experiment-manifest/v1alpha",
        "promotion-decision.schema.json": "promotion-decision/v1alpha",
    }

    assert {path.name for path in SCHEMA_ROOT.glob("*.json")} == set(expected)
    for filename, version in expected.items():
        schema = _json(SCHEMA_ROOT / filename)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        properties = schema["properties"]
        assert isinstance(properties, dict)
        schema_version = properties["schema_version"]
        assert isinstance(schema_version, dict)
        assert schema_version["const"] == version


def test_canonical_json_is_key_sorted_compact_utf8_and_newline_terminated() -> None:
    first = canonical_json_bytes({"z": 1, "á": "ação", "a": [3, 2, 1]})
    second = canonical_json_bytes({"a": [3, 2, 1], "á": "ação", "z": 1})

    assert first == second
    assert first == '{"a":[3,2,1],"z":1,"á":"ação"}\n'.encode()


def test_canonical_smoke_reads_real_bytes_for_all_28_fixtures() -> None:
    prepared = prepare_experiment(REPO_ROOT, SMOKE_MANIFEST)

    assert len(prepared.selected_fixtures) == 28
    results = run_integrity_probe(REPO_ROOT, prepared, time.monotonic() + 30)

    assert len(results) == 28
    assert [result["fixture_id"] for result in results] == sorted(
        result["fixture_id"] for result in results
    )
    assert {result["status"] for result in results} == {"SUCCEEDED"}
    assert {result["reason_code"] for result in results} == {"INTEGRITY_OK"}
    assert all(result["file"]["size_bytes"] > 0 for result in results)
    assert all(result["ground_truth"]["size_bytes"] > 0 for result in results)


def test_smoke_is_evidence_only_and_cannot_encode_promotion() -> None:
    manifest = _json(SMOKE_MANIFEST)

    assert manifest["candidate"] == {
        "id": "integrity_probe/v1",
        "configuration": {"verify_ground_truth": True},
    }
    assert manifest["capability"] == "harness_integrity"
    assert "promotion_decision" not in manifest
    assert "recommendation" not in manifest
