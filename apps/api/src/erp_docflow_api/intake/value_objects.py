"""Tipos de valor canônicos do intake PDF-first."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID

from .errors import IntakeDomainError

DOCUMENT_INTAKE_OPERATION: Final = "document_intake"
DOCUMENT_INTAKE_FINGERPRINT_VERSION: Final = "document-intake-v1"
UPLOAD_SOURCE_CHANNEL: Final = "upload"
DEVELOPMENT_SYNTHETIC_CLASSIFICATION: Final = "development_synthetic"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MIME_TOKEN_RE = re.compile(
    r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+/[!#$%&'*+.^_`|~0-9A-Za-z-]+$"
)


class MimeMismatch(StrEnum):
    """Representação explícita da divergência MIME tri-state."""

    MATCH = "match"
    MISMATCH = "mismatch"
    INDETERMINATE = "indeterminate"

    @property
    def database_value(self) -> bool | None:
        if self is MimeMismatch.MATCH:
            return False
        if self is MimeMismatch.MISMATCH:
            return True
        return None

    @classmethod
    def from_database_value(cls, value: bool | None) -> MimeMismatch:
        if value is True:
            return cls.MISMATCH
        if value is False:
            return cls.MATCH
        return cls.INDETERMINATE


def require_sha256(value: str, *, field_name: str = "sha256") -> str:
    """Aceita apenas SHA-256 hexadecimal minúsculo."""

    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise IntakeDomainError(
            f"{field_name} must contain exactly 64 lowercase hexadecimal characters"
        )
    return value


def require_positive_byte_size(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise IntakeDomainError("byte_size must be a positive integer")
    return value


def normalize_filename(value: str) -> str:
    """Normaliza o nome em NFC sem alterar espaços ou caixa semanticamente."""

    if not isinstance(value, str) or not value:
        raise IntakeDomainError("original_filename must not be empty")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or any(unicodedata.category(char) == "Cc" for char in normalized):
        raise IntakeDomainError("original_filename contains control characters")
    return normalized


def normalize_mime(value: str | None) -> str | None:
    """Normaliza um media type para comparação, preservando `None`.

    Parâmetros não fazem parte da identidade de formato do intake. O valor bruto
    continua disponível separadamente no descritor e no FileObject.
    """

    if value is None:
        return None
    if not isinstance(value, str):
        raise IntakeDomainError("MIME value must be text or null")
    media_type = value.split(";", maxsplit=1)[0].strip().lower()
    if not media_type:
        return None
    if _MIME_TOKEN_RE.fullmatch(media_type) is None:
        raise IntakeDomainError("MIME value must be a valid type/subtype")
    return media_type


def determine_mime_mismatch(
    advertised_mime: str | None,
    intake_detected_mime: str | None,
) -> MimeMismatch:
    advertised = normalize_mime(advertised_mime)
    detected = normalize_mime(intake_detected_mime)
    if advertised is None or detected is None:
        return MimeMismatch.INDETERMINATE
    if advertised == detected:
        return MimeMismatch.MATCH
    return MimeMismatch.MISMATCH


def normalize_source_channel(value: str) -> str:
    if not isinstance(value, str):
        raise IntakeDomainError("source_channel must be text")
    normalized = unicodedata.normalize("NFC", value).strip().lower()
    if normalized != UPLOAD_SOURCE_CHANNEL:
        raise IntakeDomainError("source_channel must be upload in this slice")
    return normalized


def normalize_utc(value: datetime, *, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise IntakeDomainError(f"{field_name} must be timezone-aware")
    return value.astimezone(UTC)


def require_uuid(value: UUID, *, field_name: str) -> UUID:
    if not isinstance(value, UUID):
        raise IntakeDomainError(f"{field_name} must be a UUID")
    return value


def require_nonempty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise IntakeDomainError(f"{field_name} must not be empty")
    if any(unicodedata.category(char) == "Cc" for char in value):
        raise IntakeDomainError(f"{field_name} contains control characters")
    return value


@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    """Digest seguro de uma chave opaca validada.

    Use :meth:`from_raw`; o texto original é deliberadamente descartado.
    """

    digest: str

    def __post_init__(self) -> None:
        require_sha256(self.digest, field_name="idempotency_key_digest")

    @classmethod
    def from_raw(cls, raw_key: str) -> IdempotencyKey:
        if not isinstance(raw_key, str):
            raise IntakeDomainError("idempotency key must be text")
        if not 1 <= len(raw_key) <= 128:
            raise IntakeDomainError(
                "idempotency key must contain between 1 and 128 characters"
            )
        if any(unicodedata.category(char).startswith("C") for char in raw_key):
            raise IntakeDomainError("idempotency key contains control characters")
        return cls(hashlib.sha256(raw_key.encode("utf-8")).hexdigest())


@dataclass(frozen=True, slots=True)
class IntakeFingerprint:
    """Fingerprint canônico e versionado da requisição de intake."""

    content_sha256: str
    byte_size: int
    advertised_mime: str | None
    original_filename: str
    source_channel: str = UPLOAD_SOURCE_CHANNEL
    version: str = DOCUMENT_INTAKE_FINGERPRINT_VERSION

    def __post_init__(self) -> None:
        if self.version != DOCUMENT_INTAKE_FINGERPRINT_VERSION:
            raise IntakeDomainError(
                f"fingerprint version must be {DOCUMENT_INTAKE_FINGERPRINT_VERSION}"
            )
        object.__setattr__(self, "content_sha256", require_sha256(self.content_sha256))
        object.__setattr__(
            self,
            "byte_size",
            require_positive_byte_size(self.byte_size),
        )
        object.__setattr__(
            self, "advertised_mime", normalize_mime(self.advertised_mime)
        )
        object.__setattr__(
            self, "original_filename", normalize_filename(self.original_filename)
        )
        object.__setattr__(
            self, "source_channel", normalize_source_channel(self.source_channel)
        )

    @property
    def canonical_payload(self) -> dict[str, int | str | None]:
        return {
            "advertised_mime": self.advertised_mime,
            "byte_size": self.byte_size,
            "content_sha256": self.content_sha256,
            "original_filename": self.original_filename,
            "source_channel": self.source_channel,
            "version": self.version,
        }

    @property
    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json.encode("utf-8")).hexdigest()
