"""Entidades puras que referenciam binários fora do PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from erp_docflow_api.intake.errors import DescriptorVerificationError
from erp_docflow_api.intake.value_objects import (
    DEVELOPMENT_SYNTHETIC_CLASSIFICATION,
    MimeMismatch,
    determine_mime_mismatch,
    normalize_filename,
    normalize_mime,
    normalize_utc,
    require_nonempty_text,
    require_positive_byte_size,
    require_sha256,
    require_uuid,
)


class IntegrityState(StrEnum):
    VERIFIED = "VERIFIED"


class FileRole(StrEnum):
    ORIGINAL = "ORIGINAL"


@dataclass(frozen=True, slots=True)
class VerifiedOriginalDescriptor:
    """Metadados fornecidos depois da verificação real feita pela #40.

    Nesta slice o tipo só valida o contrato. Sua existência não afirma que o
    objeto está armazenado; o chamador futuro é responsável por essa prova.
    """

    storage_bucket: str
    storage_key: str
    sha256: str
    byte_size: int
    original_filename: str
    advertised_mime_raw: str | None
    intake_detected_mime: str | None
    verified_at: datetime
    integrity_state: IntegrityState = IntegrityState.VERIFIED

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "storage_bucket",
            require_nonempty_text(self.storage_bucket, field_name="storage_bucket"),
        )
        object.__setattr__(
            self,
            "storage_key",
            require_nonempty_text(self.storage_key, field_name="storage_key"),
        )
        object.__setattr__(self, "sha256", require_sha256(self.sha256))
        object.__setattr__(
            self,
            "byte_size",
            require_positive_byte_size(self.byte_size),
        )
        object.__setattr__(
            self, "original_filename", normalize_filename(self.original_filename)
        )
        normalize_mime(self.advertised_mime_raw)
        object.__setattr__(
            self, "intake_detected_mime", normalize_mime(self.intake_detected_mime)
        )
        object.__setattr__(
            self,
            "verified_at",
            normalize_utc(self.verified_at, field_name="verified_at"),
        )
        if self.integrity_state is not IntegrityState.VERIFIED:
            raise DescriptorVerificationError(
                "original descriptor must have VERIFIED integrity"
            )

    @property
    def advertised_mime(self) -> str | None:
        return normalize_mime(self.advertised_mime_raw)

    @property
    def mime_mismatch(self) -> MimeMismatch:
        return determine_mime_mismatch(
            self.advertised_mime,
            self.intake_detected_mime,
        )


@dataclass(frozen=True, slots=True)
class FileObject:
    id: UUID
    tenant_id: UUID
    document_version_id: UUID
    storage_bucket: str
    storage_key: str
    sha256: str
    byte_size: int
    original_filename: str
    advertised_mime_raw: str | None
    intake_detected_mime: str | None
    verified_at: datetime
    created_at: datetime
    role: FileRole = FileRole.ORIGINAL
    integrity_state: IntegrityState = IntegrityState.VERIFIED
    classification: str = DEVELOPMENT_SYNTHETIC_CLASSIFICATION

    def __post_init__(self) -> None:
        require_uuid(self.id, field_name="file_object.id")
        require_uuid(self.tenant_id, field_name="file_object.tenant_id")
        require_uuid(
            self.document_version_id,
            field_name="file_object.document_version_id",
        )
        descriptor = VerifiedOriginalDescriptor(
            storage_bucket=self.storage_bucket,
            storage_key=self.storage_key,
            sha256=self.sha256,
            byte_size=self.byte_size,
            original_filename=self.original_filename,
            advertised_mime_raw=self.advertised_mime_raw,
            intake_detected_mime=self.intake_detected_mime,
            verified_at=self.verified_at,
            integrity_state=self.integrity_state,
        )
        object.__setattr__(self, "storage_bucket", descriptor.storage_bucket)
        object.__setattr__(self, "storage_key", descriptor.storage_key)
        object.__setattr__(self, "sha256", descriptor.sha256)
        object.__setattr__(self, "byte_size", descriptor.byte_size)
        object.__setattr__(self, "original_filename", descriptor.original_filename)
        object.__setattr__(
            self, "intake_detected_mime", descriptor.intake_detected_mime
        )
        object.__setattr__(self, "verified_at", descriptor.verified_at)
        object.__setattr__(
            self, "created_at", normalize_utc(self.created_at, field_name="created_at")
        )
        if self.role is not FileRole.ORIGINAL:
            raise DescriptorVerificationError(
                "file role must be ORIGINAL in this slice"
            )
        if self.classification != DEVELOPMENT_SYNTHETIC_CLASSIFICATION:
            raise DescriptorVerificationError(
                "file classification must be development_synthetic"
            )

    @property
    def advertised_mime(self) -> str | None:
        return normalize_mime(self.advertised_mime_raw)

    @property
    def mime_mismatch(self) -> MimeMismatch:
        return determine_mime_mismatch(
            self.advertised_mime,
            self.intake_detected_mime,
        )
