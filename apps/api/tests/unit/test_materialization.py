from __future__ import annotations

import dataclasses
from datetime import UTC, datetime
from uuid import UUID

import pytest

from erp_docflow_api.documents import DocumentState
from erp_docflow_api.files import IntegrityState, VerifiedOriginalDescriptor
from erp_docflow_api.intake import (
    DescriptorVerificationError,
    FinalizationDisposition,
    IdempotencyResolutionKind,
    IntakeOccurrence,
    IntakeOccurrenceState,
    InvalidStateTransition,
    MaterializationReplayError,
    MaterializationResultIds,
    MimeMismatch,
    finalize_verified_original,
    plan_finalization,
)

MATERIALIZED_AT = datetime(2026, 8, 2, 12, 0, 10, tzinfo=UTC)


def test_verified_descriptor_normalizes_nfc_and_preserves_mime_observations() -> None:
    descriptor = VerifiedOriginalDescriptor(
        storage_bucket="originals",
        storage_key="opaque/key",
        sha256="a" * 64,
        byte_size=1,
        original_filename="cafe\u0301.pdf",
        advertised_mime_raw="Application/PDF; charset=binary",
        intake_detected_mime="IMAGE/PNG",
        verified_at=MATERIALIZED_AT,
    )

    assert descriptor.original_filename == "café.pdf"
    assert descriptor.advertised_mime_raw == "Application/PDF; charset=binary"
    assert descriptor.advertised_mime == "application/pdf"
    assert descriptor.intake_detected_mime == "image/png"
    assert descriptor.mime_mismatch is MimeMismatch.MISMATCH
    assert descriptor.integrity_state is IntegrityState.VERIFIED


@pytest.mark.parametrize(
    "changes",
    [
        {"integrity_state": "UNVERIFIED"},
        {"sha256": "A" * 64},
        {"byte_size": 0},
        {"advertised_mime_raw": "not a mime"},
        {"verified_at": datetime(2026, 8, 2, 12, 0)},
    ],
)
def test_descriptor_rejects_unverified_or_invalid_metadata(changes: dict) -> None:
    values = {
        "storage_bucket": "originals",
        "storage_key": "opaque/key",
        "sha256": "a" * 64,
        "byte_size": 1,
        "original_filename": "invoice.pdf",
        "advertised_mime_raw": "application/pdf",
        "intake_detected_mime": "application/pdf",
        "verified_at": MATERIALIZED_AT,
    }
    values.update(changes)

    with pytest.raises(ValueError):
        VerifiedOriginalDescriptor(**values)


def test_plan_and_finalize_build_one_consistent_atomic_unit(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    plan = plan_finalization(verified_occurrence, descriptor)
    assert plan.disposition is FinalizationDisposition.CREATE
    assert plan.result_ids is None

    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )

    assert materialization.occurrence.state is IntakeOccurrenceState.COMPLETED
    assert materialization.occurrence.result_ids == result_ids
    assert materialization.document_envelope.state is DocumentState.INSPECTION_PENDING
    assert (
        materialization.document_envelope.current_version_id
        == result_ids.document_version_id
    )
    assert materialization.document_version.version_number == 1
    assert materialization.document_version.previous_version_id is None
    assert materialization.file_object.sha256 == descriptor.sha256
    assert materialization.file_object.mime_mismatch is MimeMismatch.MATCH
    assert materialization.audit_event.intake_occurrence_id == verified_occurrence.id
    assert (
        materialization.audit_event.correlation_id
        == verified_occurrence.correlation_id
    )
    assert (
        materialization.audit_event.resulting_state
        is DocumentState.INSPECTION_PENDING
    )
    assert len(
        {
            materialization.occurrence.tenant_id,
            materialization.document_envelope.tenant_id,
            materialization.document_version.tenant_id,
            materialization.file_object.tenant_id,
            materialization.audit_event.tenant_id,
        }
    ) == 1

    replay_resolution = materialization.occurrence.bind_or_compare_fingerprint(
        verified_occurrence.fingerprint,
        at=materialization.occurrence.updated_at,
    )
    assert replay_resolution.kind is IdempotencyResolutionKind.REPLAY_COMPLETED
    replay_plan = plan_finalization(materialization.occurrence, descriptor)
    assert replay_plan.disposition is FinalizationDisposition.REPLAY
    assert replay_plan.result_ids == result_ids
    replayed = finalize_verified_original(
        materialization.occurrence,
        descriptor,
        existing_materialization=materialization,
    )
    assert replayed is materialization


def test_completed_replay_cannot_allocate_new_facts(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )

    with pytest.raises(MaterializationReplayError):
        finalize_verified_original(materialization.occurrence, descriptor)
    with pytest.raises(MaterializationReplayError):
        finalize_verified_original(
            materialization.occurrence,
            descriptor,
            result_ids=result_ids,
            occurred_at=MATERIALIZED_AT,
            existing_materialization=materialization,
        )
    with pytest.raises(InvalidStateTransition):
        materialization.occurrence.transition(
            IntakeOccurrenceState.RECEIVING,
            at=MATERIALIZED_AT,
        )


def test_descriptor_must_equal_bound_fingerprint(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
) -> None:
    changed = dataclasses.replace(descriptor, byte_size=descriptor.byte_size + 1)

    with pytest.raises(DescriptorVerificationError):
        plan_finalization(verified_occurrence, changed)


def test_descriptor_must_equal_bound_candidate_storage(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
) -> None:
    changed = dataclasses.replace(descriptor, storage_key="other/opaque/key")

    with pytest.raises(DescriptorVerificationError, match="candidate storage"):
        plan_finalization(verified_occurrence, changed)


def test_only_verified_occurrence_can_materialize(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
) -> None:
    receiving = dataclasses.replace(
        verified_occurrence,
        state=IntakeOccurrenceState.RECEIVING,
    )

    with pytest.raises(InvalidStateTransition):
        plan_finalization(receiving, descriptor)


def test_same_binary_with_other_key_remains_a_distinct_materialization(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    other_occurrence = dataclasses.replace(
        verified_occurrence,
        id=UUID("30000000-0000-0000-0000-000000000002"),
        idempotency_key_digest="b" * 64,
        correlation_id=UUID("40000000-0000-0000-0000-000000000002"),
    )
    other_ids = MaterializationResultIds(
        document_envelope_id=UUID("50000000-0000-0000-0000-000000000002"),
        document_version_id=UUID("60000000-0000-0000-0000-000000000002"),
        file_object_id=UUID("70000000-0000-0000-0000-000000000002"),
        audit_event_id=UUID("80000000-0000-0000-0000-000000000002"),
    )

    first = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )
    second = finalize_verified_original(
        other_occurrence,
        descriptor,
        result_ids=other_ids,
        occurred_at=MATERIALIZED_AT,
    )

    assert first.file_object.sha256 == second.file_object.sha256
    assert first.occurrence.id != second.occurrence.id
    assert first.document_envelope.id != second.document_envelope.id
    assert first.audit_event.id != second.audit_event.id


def test_audit_event_and_original_entities_are_immutable(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        materialization.audit_event.source = "other"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        materialization.file_object.sha256 = "f" * 64  # type: ignore[misc]


def test_materialization_rejects_audit_links_to_other_facts(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )
    mismatched_event = dataclasses.replace(
        materialization.audit_event,
        file_object_id=UUID("70000000-0000-0000-0000-000000000099"),
    )

    with pytest.raises(DescriptorVerificationError, match="references"):
        dataclasses.replace(materialization, audit_event=mismatched_event)


def test_materialization_rejects_non_final_envelope_state(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )
    unfinished = dataclasses.replace(
        materialization.document_envelope,
        state=DocumentState.MATERIALIZED,
    )

    with pytest.raises(DescriptorVerificationError, match="INSPECTION_PENDING"):
        dataclasses.replace(materialization, document_envelope=unfinished)


def test_materialization_rejects_original_or_actor_divergence(
    verified_occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    result_ids: MaterializationResultIds,
) -> None:
    materialization = finalize_verified_original(
        verified_occurrence,
        descriptor,
        result_ids=result_ids,
        occurred_at=MATERIALIZED_AT,
    )

    with pytest.raises(DescriptorVerificationError, match="fingerprint"):
        dataclasses.replace(
            materialization,
            file_object=dataclasses.replace(
                materialization.file_object,
                byte_size=materialization.file_object.byte_size + 1,
            ),
        )

    with pytest.raises(DescriptorVerificationError, match="actor"):
        dataclasses.replace(
            materialization,
            document_version=dataclasses.replace(
                materialization.document_version,
                created_by_actor_id=UUID(
                    "20000000-0000-0000-0000-000000000099"
                ),
            ),
        )
