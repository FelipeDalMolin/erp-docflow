"""Erros estáveis do domínio de intake documental."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


class IntakeDomainError(ValueError):
    """Base para violações de invariantes do domínio de intake."""


class InvalidStateTransition(IntakeDomainError):
    """Uma transição não pertence ao grafo autorizado da ocorrência."""


class DescriptorVerificationError(IntakeDomainError):
    """O descritor não comprova os metadados exigidos para materialização."""


class MaterializationReplayError(IntakeDomainError):
    """Um replay concluído não pode ser reconstituído com dados novos."""


@dataclass(frozen=True, slots=True)
class IdempotencyConflict(IntakeDomainError):
    """A mesma unidade idempotente recebeu outro fingerprint.

    A exceção carrega somente identificadores e digests. A chave opaca em claro
    nunca participa de mensagens, logs ou estado persistível.
    """

    occurrence_id: UUID
    existing_fingerprint_sha256: str
    presented_fingerprint_sha256: str

    code: str = "IDEMPOTENCY_CONFLICT"

    def __str__(self) -> str:
        return (
            f"{self.code}: occurrence {self.occurrence_id} already has a "
            "different intake fingerprint"
        )
