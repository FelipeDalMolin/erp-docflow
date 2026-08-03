"""Real PostgreSQL tests for idempotency and atomic materialization."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from erp_docflow_api.files import VerifiedOriginalDescriptor
from erp_docflow_api.intake import IntakeFingerprint
from erp_docflow_api.persistence.postgresql.metadata import (
    audit_events,
    document_envelopes,
    document_intake_occurrence_reasons,
    document_intake_occurrences,
    document_versions,
    file_objects,
)
from erp_docflow_api.persistence.postgresql.repositories import (
    ConcurrentUpdateError,
    FingerprintData,
    IdempotencyConflictError,
    MaterializationRepository,
    VerifiedOriginalData,
)
from erp_docflow_api.persistence.postgresql.session import PostgresqlUnitOfWork

pytestmark = pytest.mark.postgres

TENANT = UUID("10000000-0000-0000-0000-000000000001")
OTHER_TENANT = UUID("10000000-0000-0000-0000-000000000002")
ACTOR = UUID("20000000-0000-0000-0000-000000000001")
CORRELATION = UUID("30000000-0000-0000-0000-000000000001")
OCCURRENCE = UUID("40000000-0000-0000-0000-000000000001")
DIGEST = "a" * 64
CONTENT_SHA = "b" * 64


def fingerprint(*, content_sha: str = CONTENT_SHA) -> FingerprintData:
    return FingerprintData.from_domain(
        IntakeFingerprint(
            content_sha256=content_sha,
            byte_size=123,
            advertised_mime="application/pdf",
            original_filename="dev-inv001-native.pdf",
        )
    )


def descriptor(
    *,
    storage_key: str = "opaque/00000000-0000-0000-0000-000000000001",
) -> VerifiedOriginalData:
    return VerifiedOriginalData.from_domain(
        VerifiedOriginalDescriptor(
            storage_bucket="erp-docflow-originals",
            storage_key=storage_key,
            sha256=CONTENT_SHA,
            byte_size=123,
            original_filename="dev-inv001-native.pdf",
            advertised_mime_raw="application/pdf",
            intake_detected_mime="application/pdf",
            verified_at=datetime(2026, 8, 3, tzinfo=UTC),
        )
    )


def prepare_verified(
    session: Session,
    *,
    digest: str = DIGEST,
    occurrence_id: UUID = OCCURRENCE,
    candidate_storage_key: str = (
        "opaque/00000000-0000-0000-0000-000000000001"
    ),
) -> UUID:
    repository = MaterializationRepository(session)
    reserved = repository.reserve_occurrence(
        tenant_id=TENANT,
        actor_id=ACTOR,
        idempotency_key_digest=digest,
        correlation_id=CORRELATION,
        occurrence_id=occurrence_id,
    ).occurrence
    bound = repository.bind_or_compare_fingerprint(
        occurrence_id=reserved.id, tenant_id=TENANT, fingerprint=fingerprint()
    )
    receiving = repository.transition_occurrence(
        occurrence_id=bound.id,
        tenant_id=TENANT,
        target_state="RECEIVING",
        expected_lock_version=bound.lock_version,
    )
    stored = repository.transition_occurrence(
        occurrence_id=bound.id,
        tenant_id=TENANT,
        target_state="STORED_UNVERIFIED",
        expected_lock_version=receiving.lock_version,
        candidate_storage_bucket="erp-docflow-originals",
        candidate_storage_key=candidate_storage_key,
    )
    repository.transition_occurrence(
        occurrence_id=bound.id,
        tenant_id=TENANT,
        target_state="VERIFIED",
        expected_lock_version=stored.lock_version,
    )
    return reserved.id


def insert_raw_materialization(
    session: Session,
    *,
    occurrence_id: UUID,
    complete_occurrence: bool = True,
    advance_envelope: bool = True,
    event_actor_id: UUID = ACTOR,
    mime_mismatch: bool | None = False,
) -> None:
    """Exercise physical constraints without using the repository happy path."""

    envelope_id = UUID("92000000-0000-0000-0000-000000000001")
    version_id = UUID("93000000-0000-0000-0000-000000000001")
    file_id = UUID("94000000-0000-0000-0000-000000000001")
    event_id = UUID("95000000-0000-0000-0000-000000000001")
    now = datetime.now(UTC)
    original = descriptor()
    current_lock = session.scalar(
        sa.select(document_intake_occurrences.c.lock_version).where(
            document_intake_occurrences.c.id == occurrence_id
        )
    )
    assert current_lock is not None

    session.execute(
        sa.insert(document_envelopes).values(
            id=envelope_id,
            tenant_id=TENANT,
            origin_occurrence_id=occurrence_id,
            current_version_id=version_id,
            state="MATERIALIZED",
            classification="development_synthetic",
            lock_version=1,
            created_at=now,
            updated_at=now,
        )
    )
    session.execute(
        sa.insert(document_versions).values(
            id=version_id,
            tenant_id=TENANT,
            document_envelope_id=envelope_id,
            version_number=1,
            kind="ORIGINAL",
            previous_version_id=None,
            creation_reason="INTAKE_ORIGINAL",
            created_by_actor_id=ACTOR,
            created_at=now,
        )
    )
    session.execute(
        sa.insert(file_objects).values(
            id=file_id,
            tenant_id=TENANT,
            document_version_id=version_id,
            role="ORIGINAL",
            storage_bucket=original.storage_bucket,
            storage_key=original.storage_key,
            sha256=original.sha256,
            byte_size=original.byte_size,
            original_filename_nfc=original.original_filename_nfc,
            advertised_mime=original.advertised_mime,
            advertised_mime_normalized=original.advertised_mime_normalized,
            intake_detected_mime=original.intake_detected_mime,
            mime_mismatch=mime_mismatch,
            integrity_state="VERIFIED",
            classification="development_synthetic",
            verified_at=original.verified_at,
            created_at=now,
        )
    )
    session.execute(
        sa.insert(audit_events).values(
            id=event_id,
            tenant_id=TENANT,
            event_type="DOCUMENT_MATERIALIZED",
            intake_occurrence_id=occurrence_id,
            document_envelope_id=envelope_id,
            document_version_id=version_id,
            file_object_id=file_id,
            actor_id=event_actor_id,
            previous_state="MATERIALIZED",
            resulting_state="INSPECTION_PENDING",
            correlation_id=CORRELATION,
            causation_id=occurrence_id,
            source="document_intake",
            classification="development_synthetic",
            occurred_at=now,
        )
    )
    if advance_envelope:
        session.execute(
            sa.update(document_envelopes)
            .where(document_envelopes.c.id == envelope_id)
            .values(state="INSPECTION_PENDING", lock_version=2, updated_at=now)
        )
    if complete_occurrence:
        session.execute(
            sa.update(document_intake_occurrences)
            .where(document_intake_occurrences.c.id == occurrence_id)
            .values(
                state="COMPLETED",
                document_envelope_id=envelope_id,
                document_version_id=version_id,
                file_object_id=file_id,
                audit_event_id=event_id,
                completed_at=now,
                updated_at=now,
                lock_version=current_lock + 1,
            )
        )


def test_reservation_is_concurrent_and_creates_one_occurrence(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    def reserve() -> tuple[UUID, bool]:
        with postgres_session_factory() as session:
            result = MaterializationRepository(session).reserve_occurrence(
                tenant_id=TENANT,
                actor_id=ACTOR,
                idempotency_key_digest=DIGEST,
                correlation_id=CORRELATION,
            )
            session.commit()
            return result.occurrence.id, result.created

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(lambda _: reserve(), range(2)))

    assert results[0][0] == results[1][0]
    assert sorted(created for _, created in results) == [False, True]


def test_fingerprint_replay_and_conflict_preserve_first_binding(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        repository = MaterializationRepository(session)
        occurrence = repository.reserve_occurrence(
            tenant_id=TENANT,
            actor_id=ACTOR,
            idempotency_key_digest=DIGEST,
            correlation_id=CORRELATION,
        ).occurrence
        first = repository.bind_or_compare_fingerprint(
            occurrence_id=occurrence.id, tenant_id=TENANT, fingerprint=fingerprint()
        )
        replay = repository.bind_or_compare_fingerprint(
            occurrence_id=occurrence.id, tenant_id=TENANT, fingerprint=fingerprint()
        )
        assert replay.id == first.id
        with pytest.raises(IdempotencyConflictError, match="IDEMPOTENCY_CONFLICT"):
            repository.bind_or_compare_fingerprint(
                occurrence_id=occurrence.id,
                tenant_id=TENANT,
                fingerprint=fingerprint(content_sha="e" * 64),
            )

    with postgres_session_factory() as session:
        persisted = MaterializationRepository(
            session
        ).get_occurrence_by_idempotency_key(
            tenant_id=TENANT, idempotency_key_digest=DIGEST
        )
        assert persisted is not None
        assert persisted.fingerprint_sha256 == fingerprint().sha256


def test_finalization_is_atomic_and_replay_does_not_duplicate(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory.begin() as session:
        repository = MaterializationRepository(session)
        first = repository.finalize_verified_original(
            occurrence_id=occurrence_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )
        replay = repository.finalize_verified_original(
            occurrence_id=occurrence_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )
        assert replay == first
        assert first.state == "INSPECTION_PENDING"
        assert first.file_object.integrity_state == "VERIFIED"
        assert len(
            repository.list_audit_events(
                tenant_id=TENANT, occurrence_id=occurrence_id
            )
        ) == 1

    with postgres_session_factory() as session:
        for table in (
            document_envelopes,
            document_versions,
            file_objects,
            audit_events,
        ):
            assert session.scalar(sa.select(sa.func.count()).select_from(table)) == 1


def test_unit_of_work_without_commit_rolls_back_finalization(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with PostgresqlUnitOfWork(postgres_session_factory) as uow:
        assert uow.materializations is not None
        uow.materializations.finalize_verified_original(
            occurrence_id=occurrence_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )

    with postgres_session_factory() as session:
        occurrence_state = session.scalar(
            sa.select(document_intake_occurrences.c.state).where(
                document_intake_occurrences.c.id == occurrence_id
            )
        )
        assert occurrence_state == "VERIFIED"
        assert session.scalar(
            sa.select(sa.func.count()).select_from(document_envelopes)
        ) == 0
        assert session.scalar(
            sa.select(sa.func.count()).select_from(audit_events)
        ) == 0


def test_original_records_and_audit_events_reject_update_and_delete(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)
        result = MaterializationRepository(session).finalize_verified_original(
            occurrence_id=occurrence_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )

    targets = (
        (document_versions, result.version_id),
        (file_objects, result.file_object.id),
        (audit_events, result.audit_event.id),
    )
    for table, identifier in targets:
        with postgres_session_factory() as session:
            with pytest.raises(DBAPIError):
                session.execute(
                    sa.update(table)
                    .where(table.c.id == identifier)
                    .values(id=identifier)
                )
                session.commit()
            session.rollback()
        with postgres_session_factory() as session:
            with pytest.raises(DBAPIError):
                session.execute(sa.delete(table).where(table.c.id == identifier))
                session.commit()
            session.rollback()


def test_composite_foreign_key_rejects_cross_tenant_file_reference(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)
        result = MaterializationRepository(session).finalize_verified_original(
            occurrence_id=occurrence_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )

    with postgres_session_factory() as session:
        with pytest.raises(IntegrityError):
            session.execute(
                sa.insert(file_objects).values(
                    id=UUID("90000000-0000-0000-0000-000000000001"),
                    tenant_id=OTHER_TENANT,
                    document_version_id=result.version_id,
                    role="ORIGINAL",
                    storage_bucket="bucket",
                    storage_key="opaque/other",
                    sha256="f" * 64,
                    byte_size=1,
                    original_filename_nfc="synthetic.pdf",
                    advertised_mime=None,
                    advertised_mime_normalized=None,
                    intake_detected_mime=None,
                    mime_mismatch=None,
                    integrity_state="VERIFIED",
                    classification="development_synthetic",
                    verified_at=datetime.now(UTC),
                )
            )
        session.rollback()


def test_tenant_scope_hides_other_tenant_occurrence(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        MaterializationRepository(session).reserve_occurrence(
            tenant_id=TENANT,
            actor_id=ACTOR,
            idempotency_key_digest=DIGEST,
            correlation_id=CORRELATION,
        )
    with postgres_session_factory() as session:
        repository = MaterializationRepository(session)
        assert (
            repository.get_occurrence_by_idempotency_key(
                tenant_id=OTHER_TENANT, idempotency_key_digest=DIGEST
            )
            is None
        )


def test_stale_lock_and_invalid_sql_transition_are_rejected(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory() as session:
        current_lock = session.scalar(
            sa.select(document_intake_occurrences.c.lock_version).where(
                document_intake_occurrences.c.id == occurrence_id
            )
        )
        assert current_lock is not None
        with pytest.raises(ConcurrentUpdateError):
            MaterializationRepository(session).transition_occurrence(
                occurrence_id=occurrence_id,
                tenant_id=TENANT,
                target_state="RECONCILIATION_REQUIRED",
                expected_lock_version=current_lock - 1,
            )

    with postgres_session_factory() as session:
        with pytest.raises(DBAPIError):
            session.execute(
                sa.update(document_intake_occurrences)
                .where(document_intake_occurrences.c.id == occurrence_id)
                .values(
                    state="RESERVED",
                    lock_version=current_lock + 1,
                    updated_at=datetime.now(UTC),
                )
            )
            session.commit()
        session.rollback()


def test_occurrence_cannot_be_inserted_after_the_initial_reserved_state(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory() as session:
        with pytest.raises(DBAPIError):
            session.execute(
                sa.insert(document_intake_occurrences).values(
                    id=UUID("40000000-0000-0000-0000-000000000099"),
                    tenant_id=TENANT,
                    actor_id=ACTOR,
                    operation="document_intake",
                    idempotency_key_digest="9" * 64,
                    source_channel="upload",
                    correlation_id=CORRELATION,
                    state="FAILED_TERMINAL",
                    lock_version=1,
                    classification="development_synthetic",
                )
            )
        session.rollback()


def test_reason_rows_are_append_only(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    reason_id = UUID("91000000-0000-0000-0000-000000000001")
    with postgres_session_factory.begin() as session:
        repository = MaterializationRepository(session)
        occurrence = repository.reserve_occurrence(
            tenant_id=TENANT,
            actor_id=ACTOR,
            idempotency_key_digest=DIGEST,
            correlation_id=CORRELATION,
        ).occurrence
        repository.record_reason(
            tenant_id=TENANT,
            occurrence_id=occurrence.id,
            attempt_number=1,
            code="STORAGE_WRITE_FAILED",
            retryable=True,
            reason_id=reason_id,
        )

    for statement in (
        sa.update(document_intake_occurrence_reasons)
        .where(document_intake_occurrence_reasons.c.id == reason_id)
        .values(retryable=False),
        sa.delete(document_intake_occurrence_reasons).where(
            document_intake_occurrence_reasons.c.id == reason_id
        ),
    ):
        with postgres_session_factory() as session:
            with pytest.raises(DBAPIError):
                session.execute(statement)
                session.commit()
            session.rollback()


def test_incorrect_mime_mismatch_is_rejected_by_postgresql(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory() as session:
        with pytest.raises(IntegrityError):
            insert_raw_materialization(
                session,
                occurrence_id=occurrence_id,
                mime_mismatch=True,
            )
            session.commit()
        session.rollback()


def test_equal_hash_with_distinct_keys_does_not_merge_materializations(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    other_occurrence = UUID("40000000-0000-0000-0000-000000000002")
    other_key = "opaque/00000000-0000-0000-0000-000000000002"
    with postgres_session_factory.begin() as session:
        first_id = prepare_verified(session)
        second_id = prepare_verified(
            session,
            digest="d" * 64,
            occurrence_id=other_occurrence,
            candidate_storage_key=other_key,
        )

    with postgres_session_factory.begin() as session:
        repository = MaterializationRepository(session)
        first = repository.finalize_verified_original(
            occurrence_id=first_id,
            tenant_id=TENANT,
            descriptor=descriptor(),
        )
        second = repository.finalize_verified_original(
            occurrence_id=second_id,
            tenant_id=TENANT,
            descriptor=descriptor(storage_key=other_key),
        )

    assert first.file_object.sha256 == second.file_object.sha256
    assert first.occurrence.id != second.occurrence.id
    assert first.envelope_id != second.envelope_id
    assert first.audit_event.id != second.audit_event.id


def test_completed_occurrence_requires_its_matching_audit_event(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory() as session:
        with pytest.raises(IntegrityError):
            insert_raw_materialization(
                session,
                occurrence_id=occurrence_id,
                event_actor_id=UUID("20000000-0000-0000-0000-000000000099"),
            )
            session.commit()
        session.rollback()


def test_document_facts_require_the_occurrence_to_complete_atomically(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory() as session:
        insert_raw_materialization(
            session,
            occurrence_id=occurrence_id,
            complete_occurrence=False,
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_completed_materialization_requires_inspection_pending_envelope(
    postgres_session_factory: sessionmaker[Session],
) -> None:
    with postgres_session_factory.begin() as session:
        occurrence_id = prepare_verified(session)

    with postgres_session_factory() as session:
        insert_raw_materialization(
            session,
            occurrence_id=occurrence_id,
            advance_envelope=False,
        )
        with pytest.raises(DBAPIError):
            session.commit()
        session.rollback()
