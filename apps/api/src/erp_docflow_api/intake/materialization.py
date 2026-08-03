"""Planejamento e construção pura da materialização atômica."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from erp_docflow_api.audit import AuditEvent
from erp_docflow_api.documents import (
    DocumentEnvelope,
    DocumentState,
    DocumentVersion,
)
from erp_docflow_api.files import FileObject, IntegrityState, VerifiedOriginalDescriptor

from .entities import (
    IntakeOccurrence,
    IntakeOccurrenceState,
    MaterializationResultIds,
)
from .errors import (
    DescriptorVerificationError,
    InvalidStateTransition,
    MaterializationReplayError,
)
from .value_objects import normalize_utc


class FinalizationDisposition(StrEnum):
    CREATE = "CREATE"
    REPLAY = "REPLAY"


@dataclass(frozen=True, slots=True)
class FinalizationPlan:
    disposition: FinalizationDisposition
    result_ids: MaterializationResultIds | None


@dataclass(frozen=True, slots=True)
class Materialization:
    occurrence: IntakeOccurrence
    document_envelope: DocumentEnvelope
    document_version: DocumentVersion
    file_object: FileObject
    audit_event: AuditEvent

    def __post_init__(self) -> None:
        if self.occurrence.state is not IntakeOccurrenceState.COMPLETED:
            raise DescriptorVerificationError(
                "materialization must contain a completed occurrence"
            )
        result_ids = self.occurrence.result_ids
        if result_ids is None:
            raise DescriptorVerificationError("materialization result IDs are missing")
        expected = MaterializationResultIds(
            document_envelope_id=self.document_envelope.id,
            document_version_id=self.document_version.id,
            file_object_id=self.file_object.id,
            audit_event_id=self.audit_event.id,
        )
        if result_ids != expected:
            raise DescriptorVerificationError(
                "occurrence result IDs do not match materialization entities"
            )
        tenant_ids = {
            self.occurrence.tenant_id,
            self.document_envelope.tenant_id,
            self.document_version.tenant_id,
            self.file_object.tenant_id,
            self.audit_event.tenant_id,
        }
        if len(tenant_ids) != 1:
            raise DescriptorVerificationError(
                "materialization cannot contain cross-tenant references"
            )
        if self.document_envelope.origin_occurrence_id != self.occurrence.id:
            raise DescriptorVerificationError("envelope occurrence reference differs")
        if self.document_envelope.current_version_id != self.document_version.id:
            raise DescriptorVerificationError("current version reference differs")
        if self.document_envelope.state is not DocumentState.INSPECTION_PENDING:
            raise DescriptorVerificationError(
                "materialized envelope must finish in INSPECTION_PENDING"
            )
        if self.document_version.document_envelope_id != self.document_envelope.id:
            raise DescriptorVerificationError("version envelope reference differs")
        if self.document_version.created_by_actor_id != self.occurrence.actor_id:
            raise DescriptorVerificationError("version actor reference differs")
        if self.file_object.document_version_id != self.document_version.id:
            raise DescriptorVerificationError("file version reference differs")
        fingerprint = self.occurrence.fingerprint
        if fingerprint is None:
            raise DescriptorVerificationError(
                "materialized occurrence must retain its fingerprint"
            )
        observed_original = (
            self.file_object.sha256,
            self.file_object.byte_size,
            self.file_object.advertised_mime,
            self.file_object.original_filename,
        )
        expected_original = (
            fingerprint.content_sha256,
            fingerprint.byte_size,
            fingerprint.advertised_mime,
            fingerprint.original_filename,
        )
        if observed_original != expected_original:
            raise DescriptorVerificationError(
                "file metadata differs from the intake fingerprint"
            )
        if (
            self.file_object.storage_bucket,
            self.file_object.storage_key,
        ) != (
            self.occurrence.candidate_storage_bucket,
            self.occurrence.candidate_storage_key,
        ):
            raise DescriptorVerificationError(
                "file storage differs from the intake candidate"
            )
        if self.audit_event.intake_occurrence_id != self.occurrence.id:
            raise DescriptorVerificationError("audit occurrence reference differs")
        audit_links = (
            self.audit_event.document_envelope_id,
            self.audit_event.document_version_id,
            self.audit_event.file_object_id,
            self.audit_event.actor_id,
            self.audit_event.correlation_id,
            self.audit_event.causation_id,
        )
        expected_audit_links = (
            self.document_envelope.id,
            self.document_version.id,
            self.file_object.id,
            self.occurrence.actor_id,
            self.occurrence.correlation_id,
            self.occurrence.id,
        )
        if audit_links != expected_audit_links:
            raise DescriptorVerificationError(
                "audit event references do not match the materialization"
            )


def _assert_descriptor_matches_occurrence(
    occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
) -> None:
    if descriptor.integrity_state is not IntegrityState.VERIFIED:
        raise DescriptorVerificationError(
            "finalization requires a VERIFIED original descriptor"
        )
    fingerprint = occurrence.fingerprint
    if fingerprint is None:
        raise DescriptorVerificationError(
            "occurrence must have a bound intake fingerprint"
        )
    observed = (
        descriptor.sha256,
        descriptor.byte_size,
        descriptor.advertised_mime,
        descriptor.original_filename,
    )
    expected = (
        fingerprint.content_sha256,
        fingerprint.byte_size,
        fingerprint.advertised_mime,
        fingerprint.original_filename,
    )
    if observed != expected:
        raise DescriptorVerificationError(
            "verified descriptor differs from the bound intake fingerprint"
        )
    candidate = (
        occurrence.candidate_storage_bucket,
        occurrence.candidate_storage_key,
    )
    if candidate != (descriptor.storage_bucket, descriptor.storage_key):
        raise DescriptorVerificationError(
            "verified descriptor differs from the bound candidate storage"
        )


def plan_finalization(
    occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
) -> FinalizationPlan:
    """Decide entre criação atômica e leitura idempotente, sem efeitos."""

    _assert_descriptor_matches_occurrence(occurrence, descriptor)
    if occurrence.state is IntakeOccurrenceState.COMPLETED:
        return FinalizationPlan(
            FinalizationDisposition.REPLAY,
            occurrence.result_ids,
        )
    if occurrence.state is not IntakeOccurrenceState.VERIFIED:
        raise InvalidStateTransition(
            f"verified original cannot be finalized from {occurrence.state}"
        )
    return FinalizationPlan(FinalizationDisposition.CREATE, None)


def finalize_verified_original(
    occurrence: IntakeOccurrence,
    descriptor: VerifiedOriginalDescriptor,
    *,
    result_ids: MaterializationResultIds | None = None,
    occurred_at: datetime | None = None,
    existing_materialization: Materialization | None = None,
) -> Materialization:
    """Constrói a unidade que o repositório persistirá em uma transação.

    No replay, somente a materialização já carregada pode ser devolvida. Isso
    impede que uma repetição equivalente gere IDs ou fatos de auditoria novos.
    """

    plan = plan_finalization(occurrence, descriptor)
    if plan.disposition is FinalizationDisposition.REPLAY:
        if existing_materialization is None:
            raise MaterializationReplayError(
                "completed replay requires the persisted materialization"
            )
        if existing_materialization.occurrence != occurrence:
            raise MaterializationReplayError(
                "replayed materialization does not belong to the occurrence"
            )
        if result_ids is not None or occurred_at is not None:
            raise MaterializationReplayError(
                "completed replay cannot allocate IDs or a new timestamp"
            )
        return existing_materialization

    if result_ids is None or occurred_at is None:
        raise DescriptorVerificationError(
            "new materialization requires result IDs and occurred_at"
        )
    at = normalize_utc(occurred_at, field_name="occurred_at")
    if at < descriptor.verified_at:
        raise DescriptorVerificationError(
            "materialization cannot precede descriptor verification"
        )

    version = DocumentVersion(
        id=result_ids.document_version_id,
        tenant_id=occurrence.tenant_id,
        document_envelope_id=result_ids.document_envelope_id,
        created_by_actor_id=occurrence.actor_id,
        created_at=at,
    )
    envelope = DocumentEnvelope(
        id=result_ids.document_envelope_id,
        tenant_id=occurrence.tenant_id,
        origin_occurrence_id=occurrence.id,
        current_version_id=version.id,
        state=DocumentState.MATERIALIZED,
        created_at=at,
        updated_at=at,
    ).transition_to_inspection_pending(at=at)
    file_object = FileObject(
        id=result_ids.file_object_id,
        tenant_id=occurrence.tenant_id,
        document_version_id=version.id,
        storage_bucket=descriptor.storage_bucket,
        storage_key=descriptor.storage_key,
        sha256=descriptor.sha256,
        byte_size=descriptor.byte_size,
        original_filename=descriptor.original_filename,
        advertised_mime_raw=descriptor.advertised_mime_raw,
        intake_detected_mime=descriptor.intake_detected_mime,
        verified_at=descriptor.verified_at,
        created_at=at,
    )
    audit_event = AuditEvent(
        id=result_ids.audit_event_id,
        tenant_id=occurrence.tenant_id,
        intake_occurrence_id=occurrence.id,
        document_envelope_id=envelope.id,
        document_version_id=version.id,
        file_object_id=file_object.id,
        actor_id=occurrence.actor_id,
        correlation_id=occurrence.correlation_id,
        causation_id=occurrence.id,
        occurred_at=at,
    )
    completed_occurrence = occurrence.complete_materialization(
        result_ids=result_ids,
        at=at,
    )
    return Materialization(
        occurrence=completed_occurrence,
        document_envelope=envelope,
        document_version=version,
        file_object=file_object,
        audit_event=audit_event,
    )
