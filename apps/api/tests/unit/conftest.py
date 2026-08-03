from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from erp_docflow_api.files import VerifiedOriginalDescriptor
from erp_docflow_api.intake import (
    IdempotencyKey,
    IntakeFingerprint,
    IntakeOccurrence,
    IntakeOccurrenceState,
    MaterializationResultIds,
)

TENANT_ID = UUID("10000000-0000-0000-0000-000000000001")
ACTOR_ID = UUID("20000000-0000-0000-0000-000000000001")
OCCURRENCE_ID = UUID("30000000-0000-0000-0000-000000000001")
CORRELATION_ID = UUID("40000000-0000-0000-0000-000000000001")
NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)
VERIFIED_AT = NOW + timedelta(seconds=5)
MATERIALIZED_AT = NOW + timedelta(seconds=10)
CONTENT_SHA256 = "a" * 64


@pytest.fixture
def fingerprint() -> IntakeFingerprint:
    return IntakeFingerprint(
        content_sha256=CONTENT_SHA256,
        byte_size=4096,
        advertised_mime="application/pdf",
        original_filename="nota-fiscal.pdf",
    )


@pytest.fixture
def verified_occurrence(fingerprint: IntakeFingerprint) -> IntakeOccurrence:
    return IntakeOccurrence(
        id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        actor_id=ACTOR_ID,
        idempotency_key_digest=IdempotencyKey.from_raw("upload-001").digest,
        correlation_id=CORRELATION_ID,
        created_at=NOW,
        updated_at=VERIFIED_AT,
        fingerprint=fingerprint,
        state=IntakeOccurrenceState.VERIFIED,
        candidate_storage_bucket="erp-docflow-originals",
        candidate_storage_key="01J4Y6B3Q9T5W7X8Z0K2M4N6P8/original",
        lock_version=3,
    )


@pytest.fixture
def descriptor() -> VerifiedOriginalDescriptor:
    return VerifiedOriginalDescriptor(
        storage_bucket="erp-docflow-originals",
        storage_key="01J4Y6B3Q9T5W7X8Z0K2M4N6P8/original",
        sha256=CONTENT_SHA256,
        byte_size=4096,
        original_filename="nota-fiscal.pdf",
        advertised_mime_raw="Application/PDF; charset=binary",
        intake_detected_mime="application/pdf",
        verified_at=VERIFIED_AT,
    )


@pytest.fixture
def result_ids() -> MaterializationResultIds:
    return MaterializationResultIds(
        document_envelope_id=UUID("50000000-0000-0000-0000-000000000001"),
        document_version_id=UUID("60000000-0000-0000-0000-000000000001"),
        file_object_id=UUID("70000000-0000-0000-0000-000000000001"),
        audit_event_id=UUID("80000000-0000-0000-0000-000000000001"),
    )
