"""Contrato público do domínio de intake documental."""

from .entities import (
    IdempotencyResolution,
    IdempotencyResolutionKind,
    IntakeOccurrence,
    IntakeOccurrenceState,
    IntakeReasonCode,
    MaterializationResultIds,
)
from .errors import (
    DescriptorVerificationError,
    IdempotencyConflict,
    IntakeDomainError,
    InvalidStateTransition,
    MaterializationReplayError,
)
from .value_objects import (
    DEVELOPMENT_SYNTHETIC_CLASSIFICATION,
    DOCUMENT_INTAKE_FINGERPRINT_VERSION,
    DOCUMENT_INTAKE_OPERATION,
    UPLOAD_SOURCE_CHANNEL,
    IdempotencyKey,
    IntakeFingerprint,
    MimeMismatch,
    determine_mime_mismatch,
    normalize_filename,
    normalize_mime,
)

_MATERIALIZATION_EXPORTS = frozenset(
    {
        "FinalizationDisposition",
        "FinalizationPlan",
        "Materialization",
        "finalize_verified_original",
        "plan_finalization",
    }
)


def __getattr__(name: str) -> object:
    """Carrega a composição entre contexts sem criar ciclo de imports."""

    if name in _MATERIALIZATION_EXPORTS:
        from . import materialization

        return getattr(materialization, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "DEVELOPMENT_SYNTHETIC_CLASSIFICATION",
    "DOCUMENT_INTAKE_FINGERPRINT_VERSION",
    "DOCUMENT_INTAKE_OPERATION",
    "UPLOAD_SOURCE_CHANNEL",
    "DescriptorVerificationError",
    "FinalizationDisposition",
    "FinalizationPlan",
    "IdempotencyConflict",
    "IdempotencyKey",
    "IdempotencyResolution",
    "IdempotencyResolutionKind",
    "IntakeDomainError",
    "IntakeFingerprint",
    "IntakeOccurrence",
    "IntakeOccurrenceState",
    "IntakeReasonCode",
    "InvalidStateTransition",
    "Materialization",
    "MaterializationReplayError",
    "MaterializationResultIds",
    "MimeMismatch",
    "determine_mime_mismatch",
    "finalize_verified_original",
    "normalize_filename",
    "normalize_mime",
    "plan_finalization",
]
