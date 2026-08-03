"""Entidades documentais mínimas, independentes de persistência."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from erp_docflow_api.intake.errors import IntakeDomainError, InvalidStateTransition
from erp_docflow_api.intake.value_objects import (
    DEVELOPMENT_SYNTHETIC_CLASSIFICATION,
    normalize_utc,
    require_uuid,
)


class DocumentState(StrEnum):
    MATERIALIZED = "MATERIALIZED"
    INSPECTION_PENDING = "INSPECTION_PENDING"


class DocumentVersionKind(StrEnum):
    ORIGINAL = "ORIGINAL"


class DocumentCreationReason(StrEnum):
    INTAKE_ORIGINAL = "INTAKE_ORIGINAL"


@dataclass(frozen=True, slots=True)
class DocumentEnvelope:
    id: UUID
    tenant_id: UUID
    origin_occurrence_id: UUID
    current_version_id: UUID
    state: DocumentState
    created_at: datetime
    updated_at: datetime
    lock_version: int = 1
    classification: str = DEVELOPMENT_SYNTHETIC_CLASSIFICATION

    def __post_init__(self) -> None:
        require_uuid(self.id, field_name="document_envelope.id")
        require_uuid(self.tenant_id, field_name="document_envelope.tenant_id")
        require_uuid(
            self.origin_occurrence_id,
            field_name="document_envelope.origin_occurrence_id",
        )
        require_uuid(
            self.current_version_id,
            field_name="document_envelope.current_version_id",
        )
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
        if self.classification != DEVELOPMENT_SYNTHETIC_CLASSIFICATION:
            raise IntakeDomainError(
                "document classification must be development_synthetic"
            )

    def transition_to_inspection_pending(self, *, at: datetime) -> DocumentEnvelope:
        if self.state is not DocumentState.MATERIALIZED:
            raise InvalidStateTransition(
                f"document cannot transition from {self.state} to INSPECTION_PENDING"
            )
        changed_at = normalize_utc(at, field_name="at")
        if changed_at < self.updated_at:
            raise IntakeDomainError("at cannot precede the current updated_at")
        return replace(
            self,
            state=DocumentState.INSPECTION_PENDING,
            updated_at=changed_at,
            lock_version=self.lock_version + 1,
        )


@dataclass(frozen=True, slots=True)
class DocumentVersion:
    id: UUID
    tenant_id: UUID
    document_envelope_id: UUID
    created_by_actor_id: UUID
    created_at: datetime
    version_number: int = 1
    kind: DocumentVersionKind = DocumentVersionKind.ORIGINAL
    previous_version_id: UUID | None = None
    creation_reason: DocumentCreationReason = DocumentCreationReason.INTAKE_ORIGINAL

    def __post_init__(self) -> None:
        require_uuid(self.id, field_name="document_version.id")
        require_uuid(self.tenant_id, field_name="document_version.tenant_id")
        require_uuid(
            self.document_envelope_id,
            field_name="document_version.document_envelope_id",
        )
        require_uuid(
            self.created_by_actor_id,
            field_name="document_version.created_by_actor_id",
        )
        object.__setattr__(
            self, "created_at", normalize_utc(self.created_at, field_name="created_at")
        )
        if self.version_number != 1:
            raise IntakeDomainError("the intake original must be document version 1")
        if self.kind is not DocumentVersionKind.ORIGINAL:
            raise IntakeDomainError("the intake version kind must be ORIGINAL")
        if self.previous_version_id is not None:
            raise IntakeDomainError("the original version cannot have a predecessor")
        if self.creation_reason is not DocumentCreationReason.INTAKE_ORIGINAL:
            raise IntakeDomainError(
                "the original version creation reason must be INTAKE_ORIGINAL"
            )
