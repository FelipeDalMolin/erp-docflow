"""Evento mínimo e imutável da materialização documental."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from erp_docflow_api.documents import DocumentState
from erp_docflow_api.intake.errors import IntakeDomainError
from erp_docflow_api.intake.value_objects import (
    DEVELOPMENT_SYNTHETIC_CLASSIFICATION,
    DOCUMENT_INTAKE_OPERATION,
    normalize_utc,
    require_uuid,
)


class AuditEventType(StrEnum):
    DOCUMENT_MATERIALIZED = "DOCUMENT_MATERIALIZED"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    id: UUID
    tenant_id: UUID
    intake_occurrence_id: UUID
    document_envelope_id: UUID
    document_version_id: UUID
    file_object_id: UUID
    actor_id: UUID
    correlation_id: UUID
    causation_id: UUID
    occurred_at: datetime
    event_type: AuditEventType = AuditEventType.DOCUMENT_MATERIALIZED
    previous_state: DocumentState = DocumentState.MATERIALIZED
    resulting_state: DocumentState = DocumentState.INSPECTION_PENDING
    source: str = DOCUMENT_INTAKE_OPERATION
    classification: str = DEVELOPMENT_SYNTHETIC_CLASSIFICATION

    def __post_init__(self) -> None:
        for field_name in (
            "id",
            "tenant_id",
            "intake_occurrence_id",
            "document_envelope_id",
            "document_version_id",
            "file_object_id",
            "actor_id",
            "correlation_id",
            "causation_id",
        ):
            require_uuid(
                getattr(self, field_name),
                field_name=f"audit_event.{field_name}",
            )
        object.__setattr__(
            self,
            "occurred_at",
            normalize_utc(self.occurred_at, field_name="occurred_at"),
        )
        if self.event_type is not AuditEventType.DOCUMENT_MATERIALIZED:
            raise IntakeDomainError("unsupported audit event type")
        if self.previous_state is not DocumentState.MATERIALIZED:
            raise IntakeDomainError("materialization must start at MATERIALIZED")
        if self.resulting_state is not DocumentState.INSPECTION_PENDING:
            raise IntakeDomainError(
                "materialization must result in INSPECTION_PENDING"
            )
        if self.source != DOCUMENT_INTAKE_OPERATION:
            raise IntakeDomainError("audit event source must be document_intake")
        if self.classification != DEVELOPMENT_SYNTHETIC_CLASSIFICATION:
            raise IntakeDomainError(
                "audit event classification must be development_synthetic"
            )
