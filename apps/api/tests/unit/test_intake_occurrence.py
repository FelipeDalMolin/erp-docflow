from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from erp_docflow_api.intake import (
    IdempotencyConflict,
    IdempotencyResolutionKind,
    IntakeDomainError,
    IntakeFingerprint,
    IntakeOccurrence,
    IntakeOccurrenceState,
    InvalidStateTransition,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


_VALID_TRANSITIONS = {
    (IntakeOccurrenceState.RESERVED, IntakeOccurrenceState.RECEIVING),
    (IntakeOccurrenceState.RESERVED, IntakeOccurrenceState.FAILED_TERMINAL),
    (IntakeOccurrenceState.RECEIVING, IntakeOccurrenceState.STORED_UNVERIFIED),
    (IntakeOccurrenceState.RECEIVING, IntakeOccurrenceState.FAILED_RETRYABLE),
    (IntakeOccurrenceState.RECEIVING, IntakeOccurrenceState.FAILED_TERMINAL),
    (IntakeOccurrenceState.RECEIVING, IntakeOccurrenceState.RECONCILIATION_REQUIRED),
    (IntakeOccurrenceState.STORED_UNVERIFIED, IntakeOccurrenceState.VERIFIED),
    (IntakeOccurrenceState.STORED_UNVERIFIED, IntakeOccurrenceState.FAILED_RETRYABLE),
    (IntakeOccurrenceState.STORED_UNVERIFIED, IntakeOccurrenceState.FAILED_TERMINAL),
    (
        IntakeOccurrenceState.STORED_UNVERIFIED,
        IntakeOccurrenceState.RECONCILIATION_REQUIRED,
    ),
    (IntakeOccurrenceState.VERIFIED, IntakeOccurrenceState.RECONCILIATION_REQUIRED),
    (IntakeOccurrenceState.FAILED_RETRYABLE, IntakeOccurrenceState.RECEIVING),
    (
        IntakeOccurrenceState.FAILED_RETRYABLE,
        IntakeOccurrenceState.RECONCILIATION_REQUIRED,
    ),
}


@pytest.mark.parametrize(("source", "target"), sorted(_VALID_TRANSITIONS))
def test_every_authorized_non_completion_transition(
    verified_occurrence: IntakeOccurrence,
    source: IntakeOccurrenceState,
    target: IntakeOccurrenceState,
) -> None:
    occurrence = IntakeOccurrence(
        id=verified_occurrence.id,
        tenant_id=verified_occurrence.tenant_id,
        actor_id=verified_occurrence.actor_id,
        idempotency_key_digest=verified_occurrence.idempotency_key_digest,
        correlation_id=verified_occurrence.correlation_id,
        created_at=NOW,
        updated_at=NOW,
        fingerprint=verified_occurrence.fingerprint,
        state=source,
        candidate_storage_bucket=verified_occurrence.candidate_storage_bucket,
        candidate_storage_key=verified_occurrence.candidate_storage_key,
    )

    transitioned = occurrence.transition(target, at=NOW + timedelta(seconds=1))

    assert transitioned.state is target
    assert transitioned.lock_version == occurrence.lock_version + 1
    assert occurrence.state is source


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (IntakeOccurrenceState.RESERVED, IntakeOccurrenceState.VERIFIED),
        (IntakeOccurrenceState.RECEIVING, IntakeOccurrenceState.COMPLETED),
        (IntakeOccurrenceState.FAILED_TERMINAL, IntakeOccurrenceState.RECEIVING),
        (
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
            IntakeOccurrenceState.RECEIVING,
        ),
    ],
)
def test_invalid_or_unsafe_transition_is_rejected(
    verified_occurrence: IntakeOccurrence,
    source: IntakeOccurrenceState,
    target: IntakeOccurrenceState,
) -> None:
    occurrence = IntakeOccurrence(
        id=verified_occurrence.id,
        tenant_id=verified_occurrence.tenant_id,
        actor_id=verified_occurrence.actor_id,
        idempotency_key_digest=verified_occurrence.idempotency_key_digest,
        correlation_id=verified_occurrence.correlation_id,
        created_at=NOW,
        updated_at=NOW,
        fingerprint=verified_occurrence.fingerprint,
        state=source,
        candidate_storage_bucket=verified_occurrence.candidate_storage_bucket,
        candidate_storage_key=verified_occurrence.candidate_storage_key,
    )

    with pytest.raises(InvalidStateTransition):
        occurrence.transition(target, at=NOW)


def test_bind_compare_resume_and_conflict_preserve_existing_occurrence(
    verified_occurrence: IntakeOccurrence,
    fingerprint: IntakeFingerprint,
) -> None:
    reserved = IntakeOccurrence(
        id=verified_occurrence.id,
        tenant_id=verified_occurrence.tenant_id,
        actor_id=verified_occurrence.actor_id,
        idempotency_key_digest=verified_occurrence.idempotency_key_digest,
        correlation_id=verified_occurrence.correlation_id,
        created_at=NOW,
        updated_at=NOW,
    )
    bound = reserved.bind_or_compare_fingerprint(fingerprint, at=NOW)

    assert bound.kind is IdempotencyResolutionKind.BOUND
    assert reserved.fingerprint is None
    assert bound.occurrence.fingerprint is fingerprint
    assert bound.occurrence.lock_version == reserved.lock_version + 1
    resumed = bound.occurrence.bind_or_compare_fingerprint(fingerprint, at=NOW)
    assert resumed.kind is IdempotencyResolutionKind.RESUME
    assert resumed.occurrence is bound.occurrence

    conflicting = IntakeFingerprint(
        content_sha256="f" * 64,
        byte_size=fingerprint.byte_size,
        advertised_mime=fingerprint.advertised_mime,
        original_filename=fingerprint.original_filename,
    )
    with pytest.raises(IdempotencyConflict) as caught:
        bound.occurrence.bind_or_compare_fingerprint(conflicting, at=NOW)
    assert caught.value.code == "IDEMPOTENCY_CONFLICT"
    assert caught.value.existing_fingerprint_sha256 == fingerprint.sha256
    assert bound.occurrence.fingerprint is fingerprint


def test_occurrence_timestamps_cannot_move_backwards(
    verified_occurrence: IntakeOccurrence,
) -> None:
    with pytest.raises(IntakeDomainError, match="cannot precede"):
        verified_occurrence.transition(
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
            at=verified_occurrence.updated_at - timedelta(seconds=1),
        )
