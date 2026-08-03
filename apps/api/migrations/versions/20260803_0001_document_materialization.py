"""Create the minimum document materialization schema.

Revision ID: 20260803_0001
Revises:
Create Date: 2026-08-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260803_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = postgresql.UUID(as_uuid=True)
TIMESTAMPTZ = sa.TIMESTAMP(timezone=True)


def upgrade() -> None:
    op.create_table(
        "document_intake_occurrences",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("actor_id", UUID, nullable=False),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("idempotency_key_digest", sa.CHAR(64), nullable=False),
        sa.Column("source_channel", sa.String(32), nullable=False),
        sa.Column("correlation_id", UUID, nullable=False),
        sa.Column("fingerprint_version", sa.String(64)),
        sa.Column("fingerprint_sha256", sa.CHAR(64)),
        sa.Column("fingerprint_canonical", postgresql.JSONB()),
        sa.Column("content_sha256", sa.CHAR(64)),
        sa.Column("byte_size", sa.BigInteger()),
        sa.Column("original_filename_nfc", sa.Text()),
        sa.Column("advertised_mime", sa.Text()),
        sa.Column("advertised_mime_normalized", sa.Text()),
        sa.Column("candidate_storage_bucket", sa.Text()),
        sa.Column("candidate_storage_key", sa.Text()),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("lock_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("document_envelope_id", UUID),
        sa.Column("document_version_id", UUID),
        sa.Column("file_object_id", UUID),
        sa.Column("audit_event_id", UUID),
        sa.Column(
            "created_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("completed_at", TIMESTAMPTZ),
        sa.PrimaryKeyConstraint("id", name="pk_document_intake_occurrences"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_document_intake_occurrences_tenant_id_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "operation",
            "idempotency_key_digest",
            name="uq_document_intake_occurrences_idempotency_unit",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "id",
            "document_envelope_id",
            "document_version_id",
            name="uq_document_intake_occurrences_materialized_envelope",
        ),
        sa.CheckConstraint(
            "operation = 'document_intake'",
            name="ck_document_intake_occurrences_operation_document_intake",
        ),
        sa.CheckConstraint(
            "source_channel = 'upload'",
            name="ck_document_intake_occurrences_source_channel_upload",
        ),
        sa.CheckConstraint(
            "idempotency_key_digest ~ '^[0-9a-f]{64}$'",
            name="ck_document_intake_occurrences_idempotency_key_digest_sha256",
        ),
        sa.CheckConstraint(
            "state IN ('RESERVED', 'RECEIVING', 'STORED_UNVERIFIED', 'VERIFIED', "
            "'COMPLETED', 'FAILED_RETRYABLE', 'FAILED_TERMINAL', "
            "'RECONCILIATION_REQUIRED')",
            name="ck_document_intake_occurrences_state_allowed",
        ),
        sa.CheckConstraint(
            "lock_version >= 1",
            name="ck_document_intake_occurrences_lock_version_positive",
        ),
        sa.CheckConstraint(
            "classification = 'development_synthetic'",
            name="ck_document_intake_occurrences_classification_development_synthetic",
        ),
        sa.CheckConstraint(
            "((fingerprint_version IS NULL AND fingerprint_sha256 IS NULL "
            "AND fingerprint_canonical IS NULL AND content_sha256 IS NULL "
            "AND byte_size IS NULL AND original_filename_nfc IS NULL) OR "
            "(fingerprint_version = 'document-intake-v1' "
            "AND fingerprint_sha256 ~ '^[0-9a-f]{64}$' "
            "AND fingerprint_canonical IS NOT NULL "
            "AND content_sha256 ~ '^[0-9a-f]{64}$' "
            "AND byte_size > 0 AND original_filename_nfc <> ''))",
            name="ck_document_intake_occurrences_fingerprint_all_unbound_or_valid",
        ),
        sa.CheckConstraint(
            "((candidate_storage_bucket IS NULL AND candidate_storage_key IS NULL) OR "
            "(candidate_storage_bucket IS NOT NULL AND candidate_storage_bucket <> '' "
            "AND candidate_storage_key IS NOT NULL AND candidate_storage_key <> ''))",
            name="ck_document_intake_occurrences_candidate_storage_pair",
        ),
        sa.CheckConstraint(
            "((state = 'COMPLETED' AND document_envelope_id IS NOT NULL "
            "AND document_version_id IS NOT NULL AND file_object_id IS NOT NULL "
            "AND audit_event_id IS NOT NULL AND completed_at IS NOT NULL) OR "
            "(state <> 'COMPLETED' AND document_envelope_id IS NULL "
            "AND document_version_id IS NULL AND file_object_id IS NULL "
            "AND audit_event_id IS NULL AND completed_at IS NULL))",
            name="ck_document_intake_occurrences_completed_results_consistent",
        ),
    )

    op.create_table(
        "document_intake_occurrence_reasons",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("occurrence_id", UUID, nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("retryable", sa.Boolean(), nullable=False),
        sa.Column(
            "recorded_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_intake_occurrence_reasons"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_intake_reasons_tenant_id_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "occurrence_id",
            "attempt_number",
            "code",
            name="uq_intake_reasons_attempt_code",
        ),
        sa.CheckConstraint(
            "attempt_number > 0",
            name="ck_document_intake_occurrence_reasons_attempt_number_positive",
        ),
        sa.CheckConstraint(
            "code <> ''",
            name="ck_document_intake_occurrence_reasons_code_not_empty",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "occurrence_id"],
            [
                "document_intake_occurrences.tenant_id",
                "document_intake_occurrences.id",
            ],
            name="fk_intake_reasons_occurrence",
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "document_envelopes",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("origin_occurrence_id", UUID, nullable=False),
        sa.Column("current_version_id", UUID, nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("lock_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "created_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_envelopes"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_document_envelopes_tenant_id_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "origin_occurrence_id",
            name="uq_document_envelopes_origin_occurrence",
        ),
        sa.CheckConstraint(
            "state IN ('MATERIALIZED', 'INSPECTION_PENDING')",
            name="ck_document_envelopes_state_allowed",
        ),
        sa.CheckConstraint(
            "lock_version >= 1",
            name="ck_document_envelopes_lock_version_positive",
        ),
        sa.CheckConstraint(
            "classification = 'development_synthetic'",
            name="ck_document_envelopes_classification_development_synthetic",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "origin_occurrence_id"],
            [
                "document_intake_occurrences.tenant_id",
                "document_intake_occurrences.id",
            ],
            name="fk_document_envelopes_origin_occurrence",
            ondelete="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    op.create_table(
        "document_versions",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("document_envelope_id", UUID, nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("previous_version_id", UUID),
        sa.Column("creation_reason", sa.String(64), nullable=False),
        sa.Column("created_by_actor_id", UUID, nullable=False),
        sa.Column(
            "created_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_versions"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_document_versions_tenant_id_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "document_envelope_id",
            "id",
            name="uq_document_versions_tenant_envelope_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "document_envelope_id",
            "version_number",
            name="uq_document_versions_number",
        ),
        sa.CheckConstraint(
            "version_number = 1", name="ck_document_versions_version_number_one"
        ),
        sa.CheckConstraint(
            "kind = 'ORIGINAL'", name="ck_document_versions_kind_original"
        ),
        sa.CheckConstraint(
            "previous_version_id IS NULL",
            name="ck_document_versions_previous_version_absent",
        ),
        sa.CheckConstraint(
            "creation_reason = 'INTAKE_ORIGINAL'",
            name="ck_document_versions_creation_reason_intake_original",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_envelope_id"],
            ["document_envelopes.tenant_id", "document_envelopes.id"],
            name="fk_document_versions_envelope",
            ondelete="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    op.create_table(
        "file_objects",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("document_version_id", UUID, nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("storage_bucket", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("sha256", sa.CHAR(64), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("original_filename_nfc", sa.Text(), nullable=False),
        sa.Column("advertised_mime", sa.Text()),
        sa.Column("advertised_mime_normalized", sa.Text()),
        sa.Column("intake_detected_mime", sa.Text()),
        sa.Column("mime_mismatch", sa.Boolean()),
        sa.Column("integrity_state", sa.String(32), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("verified_at", TIMESTAMPTZ, nullable=False),
        sa.Column(
            "created_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_file_objects"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_file_objects_tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "document_version_id",
            "id",
            name="uq_file_objects_tenant_version_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "document_version_id",
            "role",
            name="uq_file_objects_version_role",
        ),
        sa.CheckConstraint("role = 'ORIGINAL'", name="ck_file_objects_role_original"),
        sa.CheckConstraint(
            "storage_bucket <> ''", name="ck_file_objects_storage_bucket_not_empty"
        ),
        sa.CheckConstraint(
            "storage_key <> ''", name="ck_file_objects_storage_key_not_empty"
        ),
        sa.CheckConstraint(
            "sha256 ~ '^[0-9a-f]{64}$'", name="ck_file_objects_sha256_lower_hex"
        ),
        sa.CheckConstraint(
            "byte_size > 0", name="ck_file_objects_byte_size_positive"
        ),
        sa.CheckConstraint(
            "original_filename_nfc <> ''", name="ck_file_objects_filename_not_empty"
        ),
        sa.CheckConstraint(
            "integrity_state = 'VERIFIED'",
            name="ck_file_objects_integrity_verified",
        ),
        sa.CheckConstraint(
            "classification = 'development_synthetic'",
            name="ck_file_objects_classification_development_synthetic",
        ),
        sa.CheckConstraint(
            "verified_at <= created_at",
            name="ck_file_objects_verified_before_created",
        ),
        sa.CheckConstraint(
            "((advertised_mime_normalized IS NULL OR intake_detected_mime IS NULL) "
            "AND mime_mismatch IS NULL) OR "
            "(advertised_mime_normalized IS NOT NULL "
            "AND intake_detected_mime IS NOT NULL "
            "AND mime_mismatch = "
            "(advertised_mime_normalized <> intake_detected_mime))",
            name="ck_file_objects_mime_mismatch_tristate",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_version_id"],
            ["document_versions.tenant_id", "document_versions.id"],
            name="fk_file_objects_version",
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", UUID, nullable=False),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("intake_occurrence_id", UUID, nullable=False),
        sa.Column("document_envelope_id", UUID, nullable=False),
        sa.Column("document_version_id", UUID, nullable=False),
        sa.Column("file_object_id", UUID, nullable=False),
        sa.Column("actor_id", UUID, nullable=False),
        sa.Column("previous_state", sa.String(32), nullable=False),
        sa.Column("resulting_state", sa.String(32), nullable=False),
        sa.Column("correlation_id", UUID, nullable=False),
        sa.Column("causation_id", UUID, nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column(
            "occurred_at", TIMESTAMPTZ, server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_audit_events_tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "document_envelope_id",
            "document_version_id",
            "file_object_id",
            "actor_id",
            "correlation_id",
            "causation_id",
            "id",
            name="uq_audit_events_materialization_identity",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "intake_occurrence_id",
            "event_type",
            name="uq_audit_events_materialization",
        ),
        sa.CheckConstraint(
            "event_type = 'DOCUMENT_MATERIALIZED'",
            name="ck_audit_events_event_type_materialized",
        ),
        sa.CheckConstraint(
            "previous_state = 'MATERIALIZED'",
            name="ck_audit_events_previous_materialized",
        ),
        sa.CheckConstraint(
            "resulting_state = 'INSPECTION_PENDING'",
            name="ck_audit_events_result_inspection_pending",
        ),
        sa.CheckConstraint(
            "causation_id = intake_occurrence_id",
            name="ck_audit_events_causation_occurrence",
        ),
        sa.CheckConstraint(
            "source = 'document_intake'",
            name="ck_audit_events_source_document_intake",
        ),
        sa.CheckConstraint(
            "classification = 'development_synthetic'",
            name="ck_audit_events_classification_development_synthetic",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "intake_occurrence_id"],
            [
                "document_intake_occurrences.tenant_id",
                "document_intake_occurrences.id",
            ],
            name="fk_audit_events_occurrence",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_envelope_id"],
            ["document_envelopes.tenant_id", "document_envelopes.id"],
            name="fk_audit_events_envelope",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_envelope_id", "document_version_id"],
            [
                "document_versions.tenant_id",
                "document_versions.document_envelope_id",
                "document_versions.id",
            ],
            name="fk_audit_events_version",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_version_id", "file_object_id"],
            [
                "file_objects.tenant_id",
                "file_objects.document_version_id",
                "file_objects.id",
            ],
            name="fk_audit_events_file",
            ondelete="RESTRICT",
        ),
    )

    op.create_foreign_key(
        "fk_document_envelopes_current_version",
        "document_envelopes",
        "document_versions",
        ["tenant_id", "id", "current_version_id"],
        ["tenant_id", "document_envelope_id", "id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_foreign_key(
        "fk_document_envelopes_completed_occurrence",
        "document_envelopes",
        "document_intake_occurrences",
        ["tenant_id", "origin_occurrence_id", "id", "current_version_id"],
        ["tenant_id", "id", "document_envelope_id", "document_version_id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_foreign_key(
        "fk_occurrence_result_envelope",
        "document_intake_occurrences",
        "document_envelopes",
        ["tenant_id", "document_envelope_id"],
        ["tenant_id", "id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_foreign_key(
        "fk_occurrence_result_version",
        "document_intake_occurrences",
        "document_versions",
        ["tenant_id", "document_envelope_id", "document_version_id"],
        ["tenant_id", "document_envelope_id", "id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_foreign_key(
        "fk_occurrence_result_file",
        "document_intake_occurrences",
        "file_objects",
        ["tenant_id", "document_version_id", "file_object_id"],
        ["tenant_id", "document_version_id", "id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )
    op.create_foreign_key(
        "fk_occurrence_result_audit_event",
        "document_intake_occurrences",
        "audit_events",
        [
            "tenant_id",
            "document_envelope_id",
            "document_version_id",
            "file_object_id",
            "actor_id",
            "correlation_id",
            "id",
            "audit_event_id",
        ],
        [
            "tenant_id",
            "document_envelope_id",
            "document_version_id",
            "file_object_id",
            "actor_id",
            "correlation_id",
            "causation_id",
            "id",
        ],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )

    op.execute(
        """
        CREATE FUNCTION erp_docflow_guard_occurrence_insert()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF NEW.state <> 'RESERVED' OR NEW.lock_version <> 1 THEN
                RAISE EXCEPTION 'intake occurrence must start reserved at version one'
                    USING ERRCODE = '23514';
            END IF;
            IF NEW.fingerprint_version IS NOT NULL
                OR NEW.fingerprint_sha256 IS NOT NULL
                OR NEW.fingerprint_canonical IS NOT NULL
                OR NEW.content_sha256 IS NOT NULL
                OR NEW.byte_size IS NOT NULL
                OR NEW.original_filename_nfc IS NOT NULL
                OR NEW.advertised_mime IS NOT NULL
                OR NEW.advertised_mime_normalized IS NOT NULL
                OR NEW.candidate_storage_bucket IS NOT NULL
                OR NEW.candidate_storage_key IS NOT NULL
                OR NEW.document_envelope_id IS NOT NULL
                OR NEW.document_version_id IS NOT NULL
                OR NEW.file_object_id IS NOT NULL
                OR NEW.audit_event_id IS NOT NULL
                OR NEW.completed_at IS NOT NULL
            THEN
                RAISE EXCEPTION 'new intake occurrence cannot publish progress'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END;
        $function$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_document_intake_occurrences_guard_insert
        BEFORE INSERT ON document_intake_occurrences
        FOR EACH ROW EXECUTE FUNCTION erp_docflow_guard_occurrence_insert()
        """
    )
    op.execute(
        """
        CREATE FUNCTION erp_docflow_guard_occurrence_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF OLD.state IN (
                'COMPLETED', 'FAILED_TERMINAL', 'RECONCILIATION_REQUIRED'
            ) THEN
                RAISE EXCEPTION 'terminal intake occurrence is immutable'
                    USING ERRCODE = '55000';
            END IF;

            IF NEW.lock_version <> OLD.lock_version + 1 THEN
                RAISE EXCEPTION 'intake lock_version must increment by one'
                    USING ERRCODE = '40001';
            END IF;
            IF NEW.updated_at < OLD.updated_at THEN
                RAISE EXCEPTION 'intake updated_at cannot move backwards'
                    USING ERRCODE = '22007';
            END IF;

            IF ROW(
                NEW.id, NEW.tenant_id, NEW.actor_id, NEW.operation,
                NEW.idempotency_key_digest, NEW.source_channel,
                NEW.correlation_id, NEW.classification, NEW.created_at
            ) IS DISTINCT FROM ROW(
                OLD.id, OLD.tenant_id, OLD.actor_id, OLD.operation,
                OLD.idempotency_key_digest, OLD.source_channel,
                OLD.correlation_id, OLD.classification, OLD.created_at
            ) THEN
                RAISE EXCEPTION 'intake occurrence identity is immutable'
                    USING ERRCODE = '55000';
            END IF;

            IF OLD.fingerprint_sha256 IS NOT NULL AND ROW(
                NEW.fingerprint_version, NEW.fingerprint_sha256,
                NEW.fingerprint_canonical, NEW.content_sha256, NEW.byte_size,
                NEW.original_filename_nfc, NEW.advertised_mime,
                NEW.advertised_mime_normalized
            ) IS DISTINCT FROM ROW(
                OLD.fingerprint_version, OLD.fingerprint_sha256,
                OLD.fingerprint_canonical, OLD.content_sha256, OLD.byte_size,
                OLD.original_filename_nfc, OLD.advertised_mime,
                OLD.advertised_mime_normalized
            ) THEN
                RAISE EXCEPTION 'bound intake fingerprint is immutable'
                    USING ERRCODE = '55000';
            END IF;

            IF OLD.candidate_storage_bucket IS NOT NULL AND ROW(
                NEW.candidate_storage_bucket, NEW.candidate_storage_key
            ) IS DISTINCT FROM ROW(
                OLD.candidate_storage_bucket, OLD.candidate_storage_key
            ) THEN
                RAISE EXCEPTION 'bound candidate storage is immutable'
                    USING ERRCODE = '55000';
            END IF;

            IF NEW.state <> OLD.state AND NOT (
                (OLD.state = 'RESERVED' AND NEW.state IN (
                    'RECEIVING', 'FAILED_TERMINAL'
                )) OR
                (OLD.state = 'RECEIVING' AND NEW.state IN (
                    'STORED_UNVERIFIED', 'FAILED_RETRYABLE',
                    'FAILED_TERMINAL', 'RECONCILIATION_REQUIRED'
                )) OR
                (OLD.state = 'STORED_UNVERIFIED' AND NEW.state IN (
                    'VERIFIED', 'FAILED_RETRYABLE', 'FAILED_TERMINAL',
                    'RECONCILIATION_REQUIRED'
                )) OR
                (OLD.state = 'VERIFIED' AND NEW.state IN (
                    'COMPLETED', 'RECONCILIATION_REQUIRED'
                )) OR
                (OLD.state = 'FAILED_RETRYABLE' AND NEW.state IN (
                    'RECEIVING', 'RECONCILIATION_REQUIRED'
                ))
            ) THEN
                RAISE EXCEPTION 'invalid intake occurrence transition'
                    USING ERRCODE = '22000';
            END IF;

            IF NEW.state IN ('STORED_UNVERIFIED', 'VERIFIED', 'COMPLETED')
                AND (
                    NEW.fingerprint_sha256 IS NULL OR
                    NEW.candidate_storage_bucket IS NULL
                )
            THEN
                RAISE EXCEPTION 'intake state requires fingerprint and candidate'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END;
        $function$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_document_intake_occurrences_guard_update
        BEFORE UPDATE ON document_intake_occurrences
        FOR EACH ROW EXECUTE FUNCTION erp_docflow_guard_occurrence_update()
        """
    )
    op.execute(
        """
        CREATE FUNCTION erp_docflow_guard_envelope_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF OLD.state <> 'MATERIALIZED'
                OR NEW.state <> 'INSPECTION_PENDING'
            THEN
                RAISE EXCEPTION 'invalid document envelope transition'
                    USING ERRCODE = '22000';
            END IF;
            IF NEW.lock_version <> OLD.lock_version + 1 THEN
                RAISE EXCEPTION 'envelope lock_version must increment by one'
                    USING ERRCODE = '40001';
            END IF;
            IF NEW.updated_at < OLD.updated_at THEN
                RAISE EXCEPTION 'envelope updated_at cannot move backwards'
                    USING ERRCODE = '22007';
            END IF;
            IF ROW(
                NEW.id, NEW.tenant_id, NEW.origin_occurrence_id,
                NEW.current_version_id, NEW.classification, NEW.created_at
            ) IS DISTINCT FROM ROW(
                OLD.id, OLD.tenant_id, OLD.origin_occurrence_id,
                OLD.current_version_id, OLD.classification, OLD.created_at
            ) THEN
                RAISE EXCEPTION 'document envelope identity is immutable'
                    USING ERRCODE = '55000';
            END IF;
            RETURN NEW;
        END;
        $function$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_document_envelopes_guard_update
        BEFORE UPDATE ON document_envelopes
        FOR EACH ROW EXECUTE FUNCTION erp_docflow_guard_envelope_update()
        """
    )
    op.execute(
        """
        CREATE FUNCTION erp_docflow_require_envelope_final_state()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            PERFORM 1
            FROM document_envelopes
            WHERE tenant_id = NEW.tenant_id
              AND id = NEW.id
              AND state = 'INSPECTION_PENDING';
            IF NOT FOUND THEN
                RAISE EXCEPTION 'document envelope must commit as inspection pending'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NULL;
        END;
        $function$
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_document_envelopes_final_state
        AFTER INSERT OR UPDATE ON document_envelopes
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION erp_docflow_require_envelope_final_state()
        """
    )

    op.execute(
        """
        CREATE FUNCTION erp_docflow_reject_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            RAISE EXCEPTION '% is immutable', TG_TABLE_NAME
                USING ERRCODE = '55000';
        END;
        $function$
        """
    )
    for table_name in (
        "document_intake_occurrence_reasons",
        "document_versions",
        "file_objects",
        "audit_events",
    ):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table_name}_immutable
            BEFORE UPDATE OR DELETE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION erp_docflow_reject_mutation()
            """
        )


def downgrade() -> None:
    op.drop_constraint(
        "fk_occurrence_result_audit_event",
        "document_intake_occurrences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_occurrence_result_file",
        "document_intake_occurrences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_occurrence_result_version",
        "document_intake_occurrences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_occurrence_result_envelope",
        "document_intake_occurrences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_document_envelopes_current_version",
        "document_envelopes",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_document_envelopes_completed_occurrence",
        "document_envelopes",
        type_="foreignkey",
    )
    op.drop_table("audit_events")
    op.drop_table("file_objects")
    op.drop_table("document_versions")
    op.drop_table("document_envelopes")
    op.drop_table("document_intake_occurrence_reasons")
    op.drop_table("document_intake_occurrences")
    op.execute("DROP FUNCTION erp_docflow_reject_mutation()")
    op.execute("DROP FUNCTION erp_docflow_require_envelope_final_state()")
    op.execute("DROP FUNCTION erp_docflow_guard_envelope_update()")
    op.execute("DROP FUNCTION erp_docflow_guard_occurrence_update()")
    op.execute("DROP FUNCTION erp_docflow_guard_occurrence_insert()")
