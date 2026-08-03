from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import pytest

from erp_docflow_api.files import VerifiedOriginalDescriptor
from erp_docflow_api.intake import IntakeFingerprint
from erp_docflow_api.persistence.postgresql.repositories import (
    FingerprintData,
    PersistenceContractError,
    VerifiedOriginalData,
)


def test_fingerprint_data_accepts_only_the_domain_canonical_digest() -> None:
    domain = IntakeFingerprint(
        content_sha256="a" * 64,
        byte_size=4096,
        advertised_mime="application/pdf",
        original_filename="synthetic.pdf",
    )
    persisted = FingerprintData.from_domain(domain)

    assert persisted.sha256 == domain.sha256
    assert dict(persisted.canonical) == domain.canonical_payload

    with pytest.raises(PersistenceContractError, match="digest"):
        dataclasses.replace(persisted, sha256="f" * 64)

    with pytest.raises(PersistenceContractError, match="canonical payload"):
        dataclasses.replace(
            persisted,
            canonical={**persisted.canonical, "byte_size": 1},
        )


def test_verified_original_data_rejects_forged_normalized_metadata() -> None:
    domain = VerifiedOriginalDescriptor(
        storage_bucket="synthetic-originals",
        storage_key="opaque/key",
        sha256="b" * 64,
        byte_size=1,
        original_filename="synthetic.pdf",
        advertised_mime_raw="text/plain",
        intake_detected_mime="text/plain",
        verified_at=datetime(2026, 8, 3, tzinfo=UTC),
    )
    persisted = VerifiedOriginalData.from_domain(domain)

    with pytest.raises(PersistenceContractError, match="inconsistent"):
        dataclasses.replace(
            persisted,
            advertised_mime_normalized="application/pdf",
            intake_detected_mime="application/pdf",
            mime_mismatch=False,
        )
