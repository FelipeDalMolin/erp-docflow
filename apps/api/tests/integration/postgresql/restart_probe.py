"""Persist and verify one deterministic metadata-only restart probe."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from uuid import UUID

from erp_docflow_api.configuration import get_database_url
from erp_docflow_api.files import VerifiedOriginalDescriptor
from erp_docflow_api.intake import IdempotencyKey, IntakeFingerprint
from erp_docflow_api.persistence.postgresql.repositories import (
    FingerprintData,
    MaterializationRepository,
    VerifiedOriginalData,
)
from erp_docflow_api.persistence.postgresql.session import (
    create_postgresql_engine,
    create_session_factory,
)

TENANT_ID = UUID("a1000000-0000-0000-0000-000000000001")
ACTOR_ID = UUID("a2000000-0000-0000-0000-000000000001")
CORRELATION_ID = UUID("a3000000-0000-0000-0000-000000000001")
OCCURRENCE_ID = UUID("a4000000-0000-0000-0000-000000000001")
IDEMPOTENCY_DIGEST = IdempotencyKey.from_raw("synthetic-restart-probe-v1").digest
CONTENT_SHA256 = "a5" * 32
STORAGE_BUCKET = "synthetic-restart-probe"
STORAGE_KEY = "opaque/a4000000-0000-0000-0000-000000000001"


def _seed(repository: MaterializationRepository) -> None:
    reservation = repository.reserve_occurrence(
        tenant_id=TENANT_ID,
        actor_id=ACTOR_ID,
        idempotency_key_digest=IDEMPOTENCY_DIGEST,
        correlation_id=CORRELATION_ID,
        occurrence_id=OCCURRENCE_ID,
    )
    if not reservation.created:
        materialization = repository.get_materialization(
            occurrence_id=OCCURRENCE_ID,
            tenant_id=TENANT_ID,
        )
        if materialization is None:
            raise RuntimeError("restart probe already exists but is not completed")
        return

    fingerprint = FingerprintData.from_domain(
        IntakeFingerprint(
            content_sha256=CONTENT_SHA256,
            byte_size=4096,
            advertised_mime="application/pdf",
            original_filename="synthetic-restart-probe.pdf",
        )
    )
    bound = repository.bind_or_compare_fingerprint(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        fingerprint=fingerprint,
    )
    receiving = repository.transition_occurrence(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        target_state="RECEIVING",
        expected_lock_version=bound.lock_version,
    )
    stored = repository.transition_occurrence(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        target_state="STORED_UNVERIFIED",
        expected_lock_version=receiving.lock_version,
        candidate_storage_bucket=STORAGE_BUCKET,
        candidate_storage_key=STORAGE_KEY,
    )
    repository.transition_occurrence(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        target_state="VERIFIED",
        expected_lock_version=stored.lock_version,
    )
    repository.finalize_verified_original(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
        descriptor=VerifiedOriginalData.from_domain(
            VerifiedOriginalDescriptor(
                storage_bucket=STORAGE_BUCKET,
                storage_key=STORAGE_KEY,
                sha256=CONTENT_SHA256,
                byte_size=4096,
                original_filename="synthetic-restart-probe.pdf",
                advertised_mime_raw="application/pdf",
                intake_detected_mime="application/pdf",
                verified_at=datetime.now(UTC),
            )
        ),
    )


def _verify(repository: MaterializationRepository) -> None:
    materialization = repository.get_materialization(
        occurrence_id=OCCURRENCE_ID,
        tenant_id=TENANT_ID,
    )
    if materialization is None:
        raise RuntimeError("completed restart probe was not recovered")
    if materialization.occurrence.state != "COMPLETED":
        raise RuntimeError("restart probe occurrence is not completed")
    if materialization.state != "INSPECTION_PENDING":
        raise RuntimeError("restart probe envelope is not inspection pending")
    if materialization.file_object.sha256 != CONTENT_SHA256:
        raise RuntimeError("restart probe file metadata changed")
    if materialization.audit_event.event_type != "DOCUMENT_MATERIALIZED":
        raise RuntimeError("restart probe audit event changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "verify"))
    args = parser.parse_args()

    engine = create_postgresql_engine(get_database_url())
    session_factory = create_session_factory(engine)
    try:
        if args.action == "seed":
            with session_factory.begin() as session:
                _seed(MaterializationRepository(session))
            print("Seeded synthetic relational restart probe.")
        else:
            with session_factory() as session:
                _verify(MaterializationRepository(session))
            print("Verified synthetic relational restart probe after restart.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
