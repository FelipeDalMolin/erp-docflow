"""Ocorrência idempotente e sua máquina de estados."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from .errors import IdempotencyConflict, IntakeDomainError, InvalidStateTransition
from .value_objects import (
    DEVELOPMENT_SYNTHETIC_CLASSIFICATION,
    DOCUMENT_INTAKE_OPERATION,
    UPLOAD_SOURCE_CHANNEL,
    IdempotencyKey,
    IntakeFingerprint,
    normalize_utc,
    require_nonempty_text,
    require_uuid,
)


class IntakeOccurrenceState(StrEnum):
    RESERVED = "RESERVED"
    RECEIVING = "RECEIVING"
    STORED_UNVERIFIED = "STORED_UNVERIFIED"
    VERIFIED = "VERIFIED"
    COMPLETED = "COMPLETED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


class IntakeReasonCode(StrEnum):
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    STORAGE_WRITE_FAILED = "STORAGE_WRITE_FAILED"
    STORAGE_READ_FAILED = "STORAGE_READ_FAILED"
    STORAGE_INTEGRITY_MISMATCH = "STORAGE_INTEGRITY_MISMATCH"
    DATABASE_WRITE_FAILED = "DATABASE_WRITE_FAILED"
    ORPHAN_OBJECT_PENDING_CLEANUP = "ORPHAN_OBJECT_PENDING_CLEANUP"


class IdempotencyResolutionKind(StrEnum):
    BOUND = "BOUND"
    RESUME = "RESUME"
    REPLAY_COMPLETED = "REPLAY_COMPLETED"


_ALLOWED_TRANSITIONS: dict[
    IntakeOccurrenceState, frozenset[IntakeOccurrenceState]
] = {
    IntakeOccurrenceState.RESERVED: frozenset(
        {
            IntakeOccurrenceState.RECEIVING,
            IntakeOccurrenceState.FAILED_TERMINAL,
        }
    ),
    IntakeOccurrenceState.RECEIVING: frozenset(
        {
            IntakeOccurrenceState.STORED_UNVERIFIED,
            IntakeOccurrenceState.FAILED_RETRYABLE,
            IntakeOccurrenceState.FAILED_TERMINAL,
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
        }
    ),
    IntakeOccurrenceState.STORED_UNVERIFIED: frozenset(
        {
            IntakeOccurrenceState.VERIFIED,
            IntakeOccurrenceState.FAILED_RETRYABLE,
            IntakeOccurrenceState.FAILED_TERMINAL,
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
        }
    ),
    IntakeOccurrenceState.VERIFIED: frozenset(
        {
            IntakeOccurrenceState.COMPLETED,
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
        }
    ),
    IntakeOccurrenceState.FAILED_RETRYABLE: frozenset(
        {
            IntakeOccurrenceState.RECEIVING,
            IntakeOccurrenceState.RECONCILIATION_REQUIRED,
        }
    ),
    IntakeOccurrenceState.COMPLETED: frozenset(),
    IntakeOccurrenceState.FAILED_TERMINAL: frozenset(),
    IntakeOccurrenceState.RECONCILIATION_REQUIRED: frozenset(),
}


def _monotonic_timestamp(value: datetime, *, current: datetime) -> datetime:
    normalized = normalize_utc(value, field_name="at")
    if normalized < current:
        raise IntakeDomainError("at cannot precede the current updated_at")
    return normalized


@dataclass(frozen=True, slots=True)
class MaterializationResultIds:
    document_envelope_id: UUID
    document_version_id: UUID
    file_object_id: UUID
    audit_event_id: UUID

    def __post_init__(self) -> None:
        values = (
            self.document_envelope_id,
            self.document_version_id,
            self.file_object_id,
            self.audit_event_id,
        )
        for field_name, value in zip(
            (
                "document_envelope_id",
                "document_version_id",
                "file_object_id",
                "audit_event_id",
            ),
            values,
            strict=True,
        ):
            require_uuid(value, field_name=field_name)
        if len(set(values)) != len(values):
            raise IntakeDomainError("materialization result IDs must be distinct")


@dataclass(frozen=True, slots=True)
class IdempotencyResolution:
    kind: IdempotencyResolutionKind
    occurrence: IntakeOccurrence


@dataclass(frozen=True, slots=True)
class IntakeOccurrence:
    id: UUID
    tenant_id: UUID
    actor_id: UUID
    idempotency_key_digest: str
    correlation_id: UUID
    created_at: datetime
    updated_at: datetime
    fingerprint: IntakeFingerprint | None = None
    state: IntakeOccurrenceState = IntakeOccurrenceState.RESERVED
    candidate_storage_bucket: str | None = None
    candidate_storage_key: str | None = None
    result_ids: MaterializationResultIds | None = None
    completed_at: datetime | None = None
    lock_version: int = 1
    operation: str = DOCUMENT_INTAKE_OPERATION
    source_channel: str = UPLOAD_SOURCE_CHANNEL
    classification: str = DEVELOPMENT_SYNTHETIC_CLASSIFICATION

    def __post_init__(self) -> None:
        require_uuid(self.id, field_name="intake_occurrence.id")
        require_uuid(self.tenant_id, field_name="intake_occurrence.tenant_id")
        require_uuid(self.actor_id, field_name="intake_occurrence.actor_id")
        require_uuid(
            self.correlation_id,
            field_name="intake_occurrence.correlation_id",
        )
        IdempotencyKey(self.idempotency_key_digest)
        object.__setattr__(
            self, "created_at", normalize_utc(self.created_at, field_name="created_at")
        )
        object.__setattr__(
            self, "updated_at", normalize_utc(self.updated_at, field_name="updated_at")
        )
        if self.updated_at < self.created_at:
            raise IntakeDomainError("updated_at cannot precede created_at")
        if (
            isinstance(self.lock_version, bool)
            or not isinstance(self.lock_version, int)
            or self.lock_version < 1
        ):
            raise IntakeDomainError("lock_version must be a positive integer")
        if self.operation != DOCUMENT_INTAKE_OPERATION:
            raise IntakeDomainError("operation must be document_intake")
        if self.source_channel != UPLOAD_SOURCE_CHANNEL:
            raise IntakeDomainError("source_channel must be upload")
        if self.classification != DEVELOPMENT_SYNTHETIC_CLASSIFICATION:
            raise IntakeDomainError(
                "occurrence classification must be development_synthetic"
            )
        if (self.candidate_storage_bucket is None) != (
            self.candidate_storage_key is None
        ):
            raise IntakeDomainError(
                "candidate storage bucket and key must be bound together"
            )
        if self.candidate_storage_bucket is not None:
            object.__setattr__(
                self,
                "candidate_storage_bucket",
                require_nonempty_text(
                    self.candidate_storage_bucket,
                    field_name="candidate_storage_bucket",
                ),
            )
            object.__setattr__(
                self,
                "candidate_storage_key",
                require_nonempty_text(
                    self.candidate_storage_key,
                    field_name="candidate_storage_key",
                ),
            )
        if self.state in {
            IntakeOccurrenceState.STORED_UNVERIFIED,
            IntakeOccurrenceState.VERIFIED,
            IntakeOccurrenceState.COMPLETED,
        } and (self.fingerprint is None or self.candidate_storage_bucket is None):
            raise IntakeDomainError(
                f"state {self.state} requires a fingerprint and candidate storage"
            )
        if self.state is IntakeOccurrenceState.COMPLETED:
            if self.result_ids is None or self.completed_at is None:
                raise IntakeDomainError(
                    "a completed occurrence must expose all materialization IDs"
                )
            object.__setattr__(
                self,
                "completed_at",
                normalize_utc(self.completed_at, field_name="completed_at"),
            )
        elif self.result_ids is not None or self.completed_at is not None:
            raise IntakeDomainError(
                "only a completed occurrence can expose materialization results"
            )

    def bind_or_compare_fingerprint(
        self,
        presented: IntakeFingerprint,
        *,
        at: datetime,
    ) -> IdempotencyResolution:
        changed_at = _monotonic_timestamp(at, current=self.updated_at)
        if self.fingerprint is None:
            bound = replace(
                self,
                fingerprint=presented,
                updated_at=changed_at,
                lock_version=self.lock_version + 1,
            )
            return IdempotencyResolution(IdempotencyResolutionKind.BOUND, bound)
        if self.fingerprint != presented:
            raise IdempotencyConflict(
                occurrence_id=self.id,
                existing_fingerprint_sha256=self.fingerprint.sha256,
                presented_fingerprint_sha256=presented.sha256,
            )
        if self.state is IntakeOccurrenceState.COMPLETED:
            kind = IdempotencyResolutionKind.REPLAY_COMPLETED
        else:
            kind = IdempotencyResolutionKind.RESUME
        return IdempotencyResolution(kind, self)

    def bind_candidate_storage(
        self,
        *,
        bucket: str,
        key: str,
        at: datetime,
    ) -> IntakeOccurrence:
        if self.state not in {
            IntakeOccurrenceState.RECEIVING,
            IntakeOccurrenceState.STORED_UNVERIFIED,
            IntakeOccurrenceState.FAILED_RETRYABLE,
        }:
            raise InvalidStateTransition(
                f"candidate storage cannot be bound in state {self.state}"
            )
        bucket = require_nonempty_text(bucket, field_name="candidate_storage_bucket")
        key = require_nonempty_text(key, field_name="candidate_storage_key")
        if self.candidate_storage_bucket is not None and (
            self.candidate_storage_bucket != bucket
            or self.candidate_storage_key != key
        ):
            raise IntakeDomainError("candidate storage is already bound differently")
        return replace(
            self,
            candidate_storage_bucket=bucket,
            candidate_storage_key=key,
            updated_at=_monotonic_timestamp(at, current=self.updated_at),
            lock_version=self.lock_version + 1,
        )

    def transition(
        self,
        target: IntakeOccurrenceState,
        *,
        at: datetime,
    ) -> IntakeOccurrence:
        if target is IntakeOccurrenceState.COMPLETED:
            raise InvalidStateTransition(
                "use complete_materialization to enter COMPLETED"
            )
        if target not in _ALLOWED_TRANSITIONS[self.state]:
            raise InvalidStateTransition(
                f"intake occurrence cannot transition from {self.state} to {target}"
            )
        return replace(
            self,
            state=target,
            updated_at=_monotonic_timestamp(at, current=self.updated_at),
            lock_version=self.lock_version + 1,
        )

    def complete_materialization(
        self,
        *,
        result_ids: MaterializationResultIds,
        at: datetime,
    ) -> IntakeOccurrence:
        if IntakeOccurrenceState.COMPLETED not in _ALLOWED_TRANSITIONS[self.state]:
            raise InvalidStateTransition(
                f"intake occurrence cannot complete from {self.state}"
            )
        completed_at = _monotonic_timestamp(at, current=self.updated_at)
        return replace(
            self,
            state=IntakeOccurrenceState.COMPLETED,
            result_ids=result_ids,
            completed_at=completed_at,
            updated_at=completed_at,
            lock_version=self.lock_version + 1,
        )
