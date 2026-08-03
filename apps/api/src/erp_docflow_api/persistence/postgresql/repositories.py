"""Transactional PostgreSQL repository for document materialization.

The public records in this module are persistence DTOs.  Application/domain
objects are adapted at the boundary, so the pure domain never imports
SQLAlchemy and the database adapter never relies on provider or storage types.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from erp_docflow_api.files import IntegrityState, VerifiedOriginalDescriptor
from erp_docflow_api.intake import IntakeFingerprint
from erp_docflow_api.persistence.postgresql.metadata import (
    audit_events,
    document_envelopes,
    document_intake_occurrence_reasons,
    document_intake_occurrences,
    document_versions,
    file_objects,
)

OPERATION = "document_intake"
SOURCE_CHANNEL = "upload"
CLASSIFICATION = "development_synthetic"

ALLOWED_TRANSITIONS: Mapping[str, frozenset[str]] = {
    "RESERVED": frozenset({"RECEIVING", "FAILED_TERMINAL"}),
    "RECEIVING": frozenset(
        {
            "STORED_UNVERIFIED",
            "FAILED_RETRYABLE",
            "FAILED_TERMINAL",
            "RECONCILIATION_REQUIRED",
        }
    ),
    "STORED_UNVERIFIED": frozenset(
        {
            "VERIFIED",
            "FAILED_RETRYABLE",
            "FAILED_TERMINAL",
            "RECONCILIATION_REQUIRED",
        }
    ),
    "VERIFIED": frozenset({"COMPLETED", "RECONCILIATION_REQUIRED"}),
    "FAILED_RETRYABLE": frozenset({"RECEIVING", "RECONCILIATION_REQUIRED"}),
    "COMPLETED": frozenset(),
    "FAILED_TERMINAL": frozenset(),
    "RECONCILIATION_REQUIRED": frozenset(),
}


class PersistenceContractError(ValueError):
    """Base class for safe persistence-boundary failures."""


class IdempotencyConflictError(PersistenceContractError):
    """The idempotency unit is already bound to another fingerprint."""

    code = "IDEMPOTENCY_CONFLICT"


class InvalidOccurrenceStateError(PersistenceContractError):
    """The requested transition or finalization is not valid."""


class ConcurrentUpdateError(PersistenceContractError):
    """An optimistic lock version did not match."""


@dataclass(frozen=True, slots=True)
class FingerprintData:
    version: str
    sha256: str
    canonical: Mapping[str, Any]
    content_sha256: str
    byte_size: int
    original_filename_nfc: str
    advertised_mime: str | None
    advertised_mime_normalized: str | None

    def __post_init__(self) -> None:
        rebuilt = IntakeFingerprint(
            version=self.version,
            content_sha256=self.content_sha256,
            byte_size=self.byte_size,
            advertised_mime=self.advertised_mime_normalized,
            original_filename=self.original_filename_nfc,
            source_channel=SOURCE_CHANNEL,
        )
        if self.advertised_mime != self.advertised_mime_normalized:
            raise PersistenceContractError(
                "fingerprint MIME must already be normalized"
            )
        if dict(self.canonical) != rebuilt.canonical_payload:
            raise PersistenceContractError(
                "fingerprint canonical payload does not match its components"
            )
        if self.sha256 != rebuilt.sha256:
            raise PersistenceContractError(
                "fingerprint digest does not match its canonical payload"
            )

    @classmethod
    def from_domain(cls, fingerprint: IntakeFingerprint) -> FingerprintData:
        """Adapt a pure fingerprint without leaking persistence into the domain."""

        return cls(
            version=fingerprint.version,
            sha256=fingerprint.sha256,
            canonical=fingerprint.canonical_payload,
            content_sha256=fingerprint.content_sha256,
            byte_size=fingerprint.byte_size,
            original_filename_nfc=fingerprint.original_filename,
            advertised_mime=fingerprint.advertised_mime,
            advertised_mime_normalized=fingerprint.advertised_mime,
        )


@dataclass(frozen=True, slots=True)
class VerifiedOriginalData:
    storage_bucket: str
    storage_key: str
    sha256: str
    byte_size: int
    original_filename_nfc: str
    advertised_mime: str | None
    advertised_mime_normalized: str | None
    intake_detected_mime: str | None
    mime_mismatch: bool | None
    integrity_state: str
    verified_at: datetime

    def __post_init__(self) -> None:
        try:
            rebuilt = VerifiedOriginalDescriptor(
                storage_bucket=self.storage_bucket,
                storage_key=self.storage_key,
                sha256=self.sha256,
                byte_size=self.byte_size,
                original_filename=self.original_filename_nfc,
                advertised_mime_raw=self.advertised_mime,
                intake_detected_mime=self.intake_detected_mime,
                verified_at=self.verified_at,
                integrity_state=IntegrityState(self.integrity_state),
            )
        except ValueError as error:
            raise PersistenceContractError(
                "verified original data violates the domain contract"
            ) from error

        expected = (
            rebuilt.storage_bucket,
            rebuilt.storage_key,
            rebuilt.sha256,
            rebuilt.byte_size,
            rebuilt.original_filename,
            rebuilt.advertised_mime_raw,
            rebuilt.advertised_mime,
            rebuilt.intake_detected_mime,
            rebuilt.mime_mismatch.database_value,
            rebuilt.integrity_state.value,
            rebuilt.verified_at,
        )
        observed = (
            self.storage_bucket,
            self.storage_key,
            self.sha256,
            self.byte_size,
            self.original_filename_nfc,
            self.advertised_mime,
            self.advertised_mime_normalized,
            self.intake_detected_mime,
            self.mime_mismatch,
            self.integrity_state,
            self.verified_at,
        )
        if observed != expected:
            raise PersistenceContractError(
                "verified original normalized metadata is inconsistent"
            )

    @classmethod
    def from_domain(
        cls, descriptor: VerifiedOriginalDescriptor
    ) -> VerifiedOriginalData:
        """Adapt the verified metadata contract supplied by the future #40."""

        return cls(
            storage_bucket=descriptor.storage_bucket,
            storage_key=descriptor.storage_key,
            sha256=descriptor.sha256,
            byte_size=descriptor.byte_size,
            original_filename_nfc=descriptor.original_filename,
            advertised_mime=descriptor.advertised_mime_raw,
            advertised_mime_normalized=descriptor.advertised_mime,
            intake_detected_mime=descriptor.intake_detected_mime,
            mime_mismatch=descriptor.mime_mismatch.database_value,
            integrity_state=descriptor.integrity_state.value,
            verified_at=descriptor.verified_at,
        )


@dataclass(frozen=True, slots=True)
class IntakeOccurrenceRecord:
    id: UUID
    tenant_id: UUID
    actor_id: UUID
    correlation_id: UUID
    idempotency_key_digest: str
    state: str
    lock_version: int
    fingerprint_sha256: str | None
    document_envelope_id: UUID | None
    document_version_id: UUID | None
    file_object_id: UUID | None
    audit_event_id: UUID | None


@dataclass(frozen=True, slots=True)
class FileObjectRecord:
    id: UUID
    tenant_id: UUID
    document_version_id: UUID
    storage_bucket: str
    storage_key: str
    sha256: str
    byte_size: int
    integrity_state: str


@dataclass(frozen=True, slots=True)
class AuditEventRecord:
    id: UUID
    tenant_id: UUID
    intake_occurrence_id: UUID
    document_envelope_id: UUID
    document_version_id: UUID
    file_object_id: UUID
    event_type: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class MaterializationRecord:
    occurrence: IntakeOccurrenceRecord
    envelope_id: UUID
    version_id: UUID
    file_object: FileObjectRecord
    audit_event: AuditEventRecord
    state: str


@dataclass(frozen=True, slots=True)
class ReservationResult:
    occurrence: IntakeOccurrenceRecord
    created: bool


def _occurrence(row: Mapping[str, Any]) -> IntakeOccurrenceRecord:
    return IntakeOccurrenceRecord(
        id=row["id"],
        tenant_id=row["tenant_id"],
        actor_id=row["actor_id"],
        correlation_id=row["correlation_id"],
        idempotency_key_digest=row["idempotency_key_digest"],
        state=row["state"],
        lock_version=row["lock_version"],
        fingerprint_sha256=row["fingerprint_sha256"],
        document_envelope_id=row["document_envelope_id"],
        document_version_id=row["document_version_id"],
        file_object_id=row["file_object_id"],
        audit_event_id=row["audit_event_id"],
    )


class MaterializationRepository:
    """Issue #39 repository operations within a caller-owned transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def reserve_occurrence(
        self,
        *,
        tenant_id: UUID,
        actor_id: UUID,
        idempotency_key_digest: str,
        correlation_id: UUID,
        occurrence_id: UUID | None = None,
    ) -> ReservationResult:
        values = {
            "id": occurrence_id or uuid4(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "operation": OPERATION,
            "idempotency_key_digest": idempotency_key_digest,
            "source_channel": SOURCE_CHANNEL,
            "correlation_id": correlation_id,
            "state": "RESERVED",
            "lock_version": 1,
            "classification": CLASSIFICATION,
        }
        statement = (
            postgresql_insert(document_intake_occurrences)
            .values(**values)
            .on_conflict_do_nothing(
                constraint="uq_document_intake_occurrences_idempotency_unit"
            )
            .returning(document_intake_occurrences)
        )
        inserted = self._session.execute(statement).mappings().one_or_none()
        if inserted is not None:
            return ReservationResult(_occurrence(inserted), created=True)

        existing = self._select_occurrence_by_digest(
            tenant_id=tenant_id,
            idempotency_key_digest=idempotency_key_digest,
            for_update=False,
        )
        if existing is None:  # defensive: a concurrent rollback can expose no row
            raise ConcurrentUpdateError("idempotency reservation disappeared")
        return ReservationResult(_occurrence(existing), created=False)

    def get_occurrence_by_idempotency_key(
        self, *, tenant_id: UUID, idempotency_key_digest: str
    ) -> IntakeOccurrenceRecord | None:
        row = self._select_occurrence_by_digest(
            tenant_id=tenant_id,
            idempotency_key_digest=idempotency_key_digest,
            for_update=False,
        )
        return _occurrence(row) if row is not None else None

    def bind_or_compare_fingerprint(
        self, *, occurrence_id: UUID, tenant_id: UUID, fingerprint: FingerprintData
    ) -> IntakeOccurrenceRecord:
        row = self._select_occurrence(
            occurrence_id=occurrence_id, tenant_id=tenant_id, for_update=True
        )
        if row is None:
            raise LookupError("intake occurrence not found")
        persisted_sha = row["fingerprint_sha256"]
        if persisted_sha is not None:
            if (
                persisted_sha != fingerprint.sha256
                or row["fingerprint_version"] != fingerprint.version
                or row["fingerprint_canonical"] != dict(fingerprint.canonical)
            ):
                raise IdempotencyConflictError(IdempotencyConflictError.code)
            return _occurrence(row)

        update = (
            sa.update(document_intake_occurrences)
            .where(
                document_intake_occurrences.c.id == occurrence_id,
                document_intake_occurrences.c.tenant_id == tenant_id,
                document_intake_occurrences.c.lock_version == row["lock_version"],
            )
            .values(
                fingerprint_version=fingerprint.version,
                fingerprint_sha256=fingerprint.sha256,
                fingerprint_canonical=dict(fingerprint.canonical),
                content_sha256=fingerprint.content_sha256,
                byte_size=fingerprint.byte_size,
                original_filename_nfc=fingerprint.original_filename_nfc,
                advertised_mime=fingerprint.advertised_mime,
                advertised_mime_normalized=fingerprint.advertised_mime_normalized,
                lock_version=row["lock_version"] + 1,
                updated_at=sa.func.now(),
            )
            .returning(document_intake_occurrences)
        )
        updated = self._session.execute(update).mappings().one_or_none()
        if updated is None:
            raise ConcurrentUpdateError("occurrence changed while binding fingerprint")
        return _occurrence(updated)

    def transition_occurrence(
        self,
        *,
        occurrence_id: UUID,
        tenant_id: UUID,
        target_state: str,
        expected_lock_version: int,
        candidate_storage_bucket: str | None = None,
        candidate_storage_key: str | None = None,
    ) -> IntakeOccurrenceRecord:
        row = self._select_occurrence(
            occurrence_id=occurrence_id, tenant_id=tenant_id, for_update=True
        )
        if row is None:
            raise LookupError("intake occurrence not found")
        if row["lock_version"] != expected_lock_version:
            raise ConcurrentUpdateError("occurrence lock_version does not match")
        current_state = row["state"]
        if target_state not in ALLOWED_TRANSITIONS.get(current_state, frozenset()):
            raise InvalidOccurrenceStateError(
                f"invalid intake transition: {current_state} -> {target_state}"
            )
        if target_state == "COMPLETED":
            raise InvalidOccurrenceStateError(
                "COMPLETED is published only by finalize_verified_original"
            )

        values: dict[str, Any] = {
            "state": target_state,
            "lock_version": expected_lock_version + 1,
            "updated_at": sa.func.now(),
        }
        if candidate_storage_bucket is not None or candidate_storage_key is not None:
            values.update(
                candidate_storage_bucket=candidate_storage_bucket,
                candidate_storage_key=candidate_storage_key,
            )
        statement = (
            sa.update(document_intake_occurrences)
            .where(
                document_intake_occurrences.c.id == occurrence_id,
                document_intake_occurrences.c.tenant_id == tenant_id,
                document_intake_occurrences.c.lock_version == expected_lock_version,
            )
            .values(**values)
            .returning(document_intake_occurrences)
        )
        updated = self._session.execute(statement).mappings().one_or_none()
        if updated is None:
            raise ConcurrentUpdateError("occurrence changed concurrently")
        return _occurrence(updated)

    def record_reason(
        self,
        *,
        tenant_id: UUID,
        occurrence_id: UUID,
        attempt_number: int,
        code: str,
        retryable: bool,
        reason_id: UUID | None = None,
    ) -> UUID:
        identifier = reason_id or uuid4()
        self._session.execute(
            sa.insert(document_intake_occurrence_reasons).values(
                id=identifier,
                tenant_id=tenant_id,
                occurrence_id=occurrence_id,
                attempt_number=attempt_number,
                code=code,
                retryable=retryable,
            )
        )
        return identifier

    def finalize_verified_original(
        self,
        *,
        occurrence_id: UUID,
        tenant_id: UUID,
        descriptor: VerifiedOriginalData,
        envelope_id: UUID | None = None,
        version_id: UUID | None = None,
        file_object_id: UUID | None = None,
        audit_event_id: UUID | None = None,
    ) -> MaterializationRecord:
        occurrence_row = self._select_occurrence(
            occurrence_id=occurrence_id, tenant_id=tenant_id, for_update=True
        )
        if occurrence_row is None:
            raise LookupError("intake occurrence not found")
        if descriptor.integrity_state != "VERIFIED":
            raise PersistenceContractError("original descriptor is not VERIFIED")
        self._compare_descriptor_to_fingerprint(occurrence_row, descriptor)
        if occurrence_row["state"] == "COMPLETED":
            materialization = self.get_materialization(
                occurrence_id=occurrence_id, tenant_id=tenant_id
            )
            if materialization is None:
                raise PersistenceContractError(
                    "completed occurrence has no materialization"
                )
            return materialization
        if occurrence_row["state"] != "VERIFIED":
            raise InvalidOccurrenceStateError(
                "occurrence must be VERIFIED before materialization"
            )

        envelope_identifier = envelope_id or uuid4()
        version_identifier = version_id or uuid4()
        file_identifier = file_object_id or uuid4()
        event_identifier = audit_event_id or uuid4()
        now = datetime.now(UTC)

        self._session.execute(
            sa.insert(document_envelopes).values(
                id=envelope_identifier,
                tenant_id=tenant_id,
                origin_occurrence_id=occurrence_id,
                current_version_id=version_identifier,
                state="MATERIALIZED",
                classification=CLASSIFICATION,
                lock_version=1,
                created_at=now,
                updated_at=now,
            )
        )
        self._session.execute(
            sa.insert(document_versions).values(
                id=version_identifier,
                tenant_id=tenant_id,
                document_envelope_id=envelope_identifier,
                version_number=1,
                kind="ORIGINAL",
                previous_version_id=None,
                creation_reason="INTAKE_ORIGINAL",
                created_by_actor_id=occurrence_row["actor_id"],
                created_at=now,
            )
        )
        self._session.execute(
            sa.insert(file_objects).values(
                id=file_identifier,
                tenant_id=tenant_id,
                document_version_id=version_identifier,
                role="ORIGINAL",
                storage_bucket=descriptor.storage_bucket,
                storage_key=descriptor.storage_key,
                sha256=descriptor.sha256,
                byte_size=descriptor.byte_size,
                original_filename_nfc=descriptor.original_filename_nfc,
                advertised_mime=descriptor.advertised_mime,
                advertised_mime_normalized=descriptor.advertised_mime_normalized,
                intake_detected_mime=descriptor.intake_detected_mime,
                mime_mismatch=descriptor.mime_mismatch,
                integrity_state=descriptor.integrity_state,
                classification=CLASSIFICATION,
                verified_at=descriptor.verified_at,
                created_at=now,
            )
        )
        self._session.execute(
            sa.insert(audit_events).values(
                id=event_identifier,
                tenant_id=tenant_id,
                event_type="DOCUMENT_MATERIALIZED",
                intake_occurrence_id=occurrence_id,
                document_envelope_id=envelope_identifier,
                document_version_id=version_identifier,
                file_object_id=file_identifier,
                actor_id=occurrence_row["actor_id"],
                previous_state="MATERIALIZED",
                resulting_state="INSPECTION_PENDING",
                correlation_id=occurrence_row["correlation_id"],
                causation_id=occurrence_id,
                source=OPERATION,
                classification=CLASSIFICATION,
                occurred_at=now,
            )
        )
        self._session.execute(
            sa.update(document_envelopes)
            .where(
                document_envelopes.c.id == envelope_identifier,
                document_envelopes.c.tenant_id == tenant_id,
                document_envelopes.c.lock_version == 1,
            )
            .values(
                state="INSPECTION_PENDING",
                lock_version=2,
                updated_at=now,
            )
        )
        updated_occurrence = self._session.execute(
            sa.update(document_intake_occurrences)
            .where(
                document_intake_occurrences.c.id == occurrence_id,
                document_intake_occurrences.c.tenant_id == tenant_id,
                document_intake_occurrences.c.lock_version
                == occurrence_row["lock_version"],
            )
            .values(
                state="COMPLETED",
                document_envelope_id=envelope_identifier,
                document_version_id=version_identifier,
                file_object_id=file_identifier,
                audit_event_id=event_identifier,
                completed_at=now,
                updated_at=now,
                lock_version=occurrence_row["lock_version"] + 1,
            )
            .returning(document_intake_occurrences.c.id)
        ).scalar_one_or_none()
        if updated_occurrence is None:
            raise ConcurrentUpdateError("occurrence changed during finalization")

        materialization = self.get_materialization(
            occurrence_id=occurrence_id, tenant_id=tenant_id
        )
        if materialization is None:
            raise PersistenceContractError("materialization could not be read back")
        return materialization

    def get_materialization(
        self, *, occurrence_id: UUID, tenant_id: UUID
    ) -> MaterializationRecord | None:
        statement = (
            sa.select(
                *document_intake_occurrences.c,
                document_envelopes.c.state.label("envelope_state"),
                file_objects.c.id.label("materialized_file_id"),
                file_objects.c.document_version_id.label("materialized_version_id"),
                file_objects.c.storage_bucket,
                file_objects.c.storage_key,
                file_objects.c.sha256.label("file_sha256"),
                file_objects.c.byte_size.label("file_byte_size"),
                file_objects.c.integrity_state,
                audit_events.c.id.label("materialization_event_id"),
                audit_events.c.event_type,
                audit_events.c.occurred_at,
            )
            .join(
                document_envelopes,
                sa.and_(
                    document_envelopes.c.tenant_id
                    == document_intake_occurrences.c.tenant_id,
                    document_envelopes.c.id
                    == document_intake_occurrences.c.document_envelope_id,
                ),
            )
            .join(
                file_objects,
                sa.and_(
                    file_objects.c.tenant_id == document_intake_occurrences.c.tenant_id,
                    file_objects.c.id == document_intake_occurrences.c.file_object_id,
                ),
            )
            .join(
                audit_events,
                sa.and_(
                    audit_events.c.tenant_id
                    == document_intake_occurrences.c.tenant_id,
                    audit_events.c.id
                    == document_intake_occurrences.c.audit_event_id,
                ),
            )
            .where(
                document_intake_occurrences.c.id == occurrence_id,
                document_intake_occurrences.c.tenant_id == tenant_id,
                document_intake_occurrences.c.state == "COMPLETED",
            )
        )
        row = self._session.execute(statement).mappings().one_or_none()
        if row is None:
            return None
        occurrence = _occurrence(row)
        file_record = FileObjectRecord(
            id=row["materialized_file_id"],
            tenant_id=tenant_id,
            document_version_id=row["materialized_version_id"],
            storage_bucket=row["storage_bucket"],
            storage_key=row["storage_key"],
            sha256=row["file_sha256"],
            byte_size=row["file_byte_size"],
            integrity_state=row["integrity_state"],
        )
        event = AuditEventRecord(
            id=row["materialization_event_id"],
            tenant_id=tenant_id,
            intake_occurrence_id=occurrence_id,
            document_envelope_id=occurrence.document_envelope_id,
            document_version_id=occurrence.document_version_id,
            file_object_id=occurrence.file_object_id,
            event_type=row["event_type"],
            occurred_at=row["occurred_at"],
        )
        return MaterializationRecord(
            occurrence=occurrence,
            envelope_id=occurrence.document_envelope_id,
            version_id=occurrence.document_version_id,
            file_object=file_record,
            audit_event=event,
            state=row["envelope_state"],
        )

    def list_audit_events(
        self, *, tenant_id: UUID, occurrence_id: UUID
    ) -> tuple[AuditEventRecord, ...]:
        rows = self._session.execute(
            sa.select(audit_events)
            .where(
                audit_events.c.tenant_id == tenant_id,
                audit_events.c.intake_occurrence_id == occurrence_id,
            )
            .order_by(audit_events.c.occurred_at, audit_events.c.id)
        ).mappings()
        return tuple(
            AuditEventRecord(
                id=row["id"],
                tenant_id=row["tenant_id"],
                intake_occurrence_id=row["intake_occurrence_id"],
                document_envelope_id=row["document_envelope_id"],
                document_version_id=row["document_version_id"],
                file_object_id=row["file_object_id"],
                event_type=row["event_type"],
                occurred_at=row["occurred_at"],
            )
            for row in rows
        )

    def _select_occurrence(
        self, *, occurrence_id: UUID, tenant_id: UUID, for_update: bool
    ) -> Mapping[str, Any] | None:
        statement = sa.select(document_intake_occurrences).where(
            document_intake_occurrences.c.id == occurrence_id,
            document_intake_occurrences.c.tenant_id == tenant_id,
        )
        if for_update:
            statement = statement.with_for_update()
        return self._session.execute(statement).mappings().one_or_none()

    def _select_occurrence_by_digest(
        self, *, tenant_id: UUID, idempotency_key_digest: str, for_update: bool
    ) -> Mapping[str, Any] | None:
        statement = sa.select(document_intake_occurrences).where(
            document_intake_occurrences.c.tenant_id == tenant_id,
            document_intake_occurrences.c.operation == OPERATION,
            document_intake_occurrences.c.idempotency_key_digest
            == idempotency_key_digest,
        )
        if for_update:
            statement = statement.with_for_update()
        return self._session.execute(statement).mappings().one_or_none()

    @staticmethod
    def _compare_descriptor_to_fingerprint(
        occurrence: Mapping[str, Any], descriptor: VerifiedOriginalData
    ) -> None:
        expected = (
            occurrence["content_sha256"],
            occurrence["byte_size"],
            occurrence["original_filename_nfc"],
            occurrence["advertised_mime_normalized"],
        )
        actual = (
            descriptor.sha256,
            descriptor.byte_size,
            descriptor.original_filename_nfc,
            descriptor.advertised_mime_normalized,
        )
        if expected != actual:
            raise PersistenceContractError(
                "verified descriptor does not match the intake fingerprint"
            )
        candidate = (
            occurrence["candidate_storage_bucket"],
            occurrence["candidate_storage_key"],
        )
        if candidate != (None, None) and candidate != (
            descriptor.storage_bucket,
            descriptor.storage_key,
        ):
            raise PersistenceContractError(
                "verified descriptor does not match candidate storage"
            )
