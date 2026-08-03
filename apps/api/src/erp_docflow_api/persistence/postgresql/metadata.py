"""SQLAlchemy metadata for the PDF-first materialization slice.

The tables intentionally use SQLAlchemy Core definitions instead of embedding
ORM concerns in the domain model.  Composite foreign keys carry ``tenant_id``
through every relationship.  PostgreSQL triggers that make original facts
immutable are installed by the Alembic migration.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.TIMESTAMP(timezone=True)

LOWER_SHA256_SQL = "VALUE ~ '^[0-9a-f]{64}$'"


document_intake_occurrences = sa.Table(
    "document_intake_occurrences",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("actor_id", uuid_type, nullable=False),
    sa.Column("operation", sa.String(64), nullable=False),
    sa.Column("idempotency_key_digest", sa.CHAR(64), nullable=False),
    sa.Column("source_channel", sa.String(32), nullable=False),
    sa.Column("correlation_id", uuid_type, nullable=False),
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
    sa.Column("lock_version", sa.Integer(), nullable=False, server_default="1"),
    sa.Column("classification", sa.String(64), nullable=False),
    sa.Column("document_envelope_id", uuid_type),
    sa.Column("document_version_id", uuid_type),
    sa.Column("file_object_id", uuid_type),
    sa.Column("audit_event_id", uuid_type),
    sa.Column(
        "created_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
    sa.Column(
        "updated_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
    sa.Column("completed_at", timestamp_type),
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
        "operation = 'document_intake'", name="operation_document_intake"
    ),
    sa.CheckConstraint("source_channel = 'upload'", name="source_channel_upload"),
    sa.CheckConstraint(
        "idempotency_key_digest ~ '^[0-9a-f]{64}$'",
        name="idempotency_key_digest_sha256",
    ),
    sa.CheckConstraint(
        "state IN ('RESERVED', 'RECEIVING', 'STORED_UNVERIFIED', 'VERIFIED', "
        "'COMPLETED', 'FAILED_RETRYABLE', 'FAILED_TERMINAL', "
        "'RECONCILIATION_REQUIRED')",
        name="state_allowed",
    ),
    sa.CheckConstraint("lock_version >= 1", name="lock_version_positive"),
    sa.CheckConstraint(
        "classification = 'development_synthetic'",
        name="classification_development_synthetic",
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
        name="fingerprint_all_unbound_or_valid",
    ),
    sa.CheckConstraint(
        "((candidate_storage_bucket IS NULL AND candidate_storage_key IS NULL) OR "
        "(candidate_storage_bucket IS NOT NULL AND candidate_storage_bucket <> '' "
        "AND candidate_storage_key IS NOT NULL AND candidate_storage_key <> ''))",
        name="candidate_storage_pair",
    ),
    sa.CheckConstraint(
        "((state = 'COMPLETED' AND document_envelope_id IS NOT NULL "
        "AND document_version_id IS NOT NULL AND file_object_id IS NOT NULL "
        "AND audit_event_id IS NOT NULL AND completed_at IS NOT NULL) OR "
        "(state <> 'COMPLETED' AND document_envelope_id IS NULL "
        "AND document_version_id IS NULL AND file_object_id IS NULL "
        "AND audit_event_id IS NULL AND completed_at IS NULL))",
        name="completed_results_consistent",
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "document_envelope_id"],
        ["document_envelopes.tenant_id", "document_envelopes.id"],
        name="fk_occurrence_result_envelope",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "document_envelope_id", "document_version_id"],
        [
            "document_versions.tenant_id",
            "document_versions.document_envelope_id",
            "document_versions.id",
        ],
        name="fk_occurrence_result_version",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "document_version_id", "file_object_id"],
        [
            "file_objects.tenant_id",
            "file_objects.document_version_id",
            "file_objects.id",
        ],
        name="fk_occurrence_result_file",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
    sa.ForeignKeyConstraint(
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
            "audit_events.tenant_id",
            "audit_events.document_envelope_id",
            "audit_events.document_version_id",
            "audit_events.file_object_id",
            "audit_events.actor_id",
            "audit_events.correlation_id",
            "audit_events.causation_id",
            "audit_events.id",
        ],
        name="fk_occurrence_result_audit_event",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
)


document_intake_occurrence_reasons = sa.Table(
    "document_intake_occurrence_reasons",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("occurrence_id", uuid_type, nullable=False),
    sa.Column("attempt_number", sa.Integer(), nullable=False),
    sa.Column("code", sa.String(64), nullable=False),
    sa.Column("retryable", sa.Boolean(), nullable=False),
    sa.Column(
        "recorded_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
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
    sa.CheckConstraint("attempt_number > 0", name="attempt_number_positive"),
    sa.CheckConstraint("code <> ''", name="code_not_empty"),
    sa.ForeignKeyConstraint(
        ["tenant_id", "occurrence_id"],
        ["document_intake_occurrences.tenant_id", "document_intake_occurrences.id"],
        name="fk_intake_reasons_occurrence",
        ondelete="RESTRICT",
    ),
)


document_envelopes = sa.Table(
    "document_envelopes",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("origin_occurrence_id", uuid_type, nullable=False),
    sa.Column("current_version_id", uuid_type, nullable=False),
    sa.Column("state", sa.String(32), nullable=False),
    sa.Column("classification", sa.String(64), nullable=False),
    sa.Column("lock_version", sa.Integer(), nullable=False, server_default="1"),
    sa.Column(
        "created_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
    sa.Column(
        "updated_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
    sa.UniqueConstraint("tenant_id", "id", name="uq_document_envelopes_tenant_id_id"),
    sa.UniqueConstraint(
        "tenant_id",
        "origin_occurrence_id",
        name="uq_document_envelopes_origin_occurrence",
    ),
    sa.CheckConstraint(
        "state IN ('MATERIALIZED', 'INSPECTION_PENDING')", name="state_allowed"
    ),
    sa.CheckConstraint("lock_version >= 1", name="lock_version_positive"),
    sa.CheckConstraint(
        "classification = 'development_synthetic'",
        name="classification_development_synthetic",
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "origin_occurrence_id"],
        ["document_intake_occurrences.tenant_id", "document_intake_occurrences.id"],
        name="fk_document_envelopes_origin_occurrence",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "id", "current_version_id"],
        [
            "document_versions.tenant_id",
            "document_versions.document_envelope_id",
            "document_versions.id",
        ],
        name="fk_document_envelopes_current_version",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "origin_occurrence_id", "id", "current_version_id"],
        [
            "document_intake_occurrences.tenant_id",
            "document_intake_occurrences.id",
            "document_intake_occurrences.document_envelope_id",
            "document_intake_occurrences.document_version_id",
        ],
        name="fk_document_envelopes_completed_occurrence",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
)


document_versions = sa.Table(
    "document_versions",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("document_envelope_id", uuid_type, nullable=False),
    sa.Column("version_number", sa.Integer(), nullable=False),
    sa.Column("kind", sa.String(32), nullable=False),
    sa.Column("previous_version_id", uuid_type),
    sa.Column("creation_reason", sa.String(64), nullable=False),
    sa.Column("created_by_actor_id", uuid_type, nullable=False),
    sa.Column(
        "created_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
    sa.UniqueConstraint("tenant_id", "id", name="uq_document_versions_tenant_id_id"),
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
    sa.CheckConstraint("version_number = 1", name="version_number_one"),
    sa.CheckConstraint("kind = 'ORIGINAL'", name="kind_original"),
    sa.CheckConstraint("previous_version_id IS NULL", name="previous_version_absent"),
    sa.CheckConstraint(
        "creation_reason = 'INTAKE_ORIGINAL'", name="creation_reason_intake_original"
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


file_objects = sa.Table(
    "file_objects",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("document_version_id", uuid_type, nullable=False),
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
    sa.Column("verified_at", timestamp_type, nullable=False),
    sa.Column(
        "created_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
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
    sa.CheckConstraint("role = 'ORIGINAL'", name="role_original"),
    sa.CheckConstraint("storage_bucket <> ''", name="storage_bucket_not_empty"),
    sa.CheckConstraint("storage_key <> ''", name="storage_key_not_empty"),
    sa.CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="sha256_lower_hex"),
    sa.CheckConstraint("byte_size > 0", name="byte_size_positive"),
    sa.CheckConstraint("original_filename_nfc <> ''", name="filename_not_empty"),
    sa.CheckConstraint("integrity_state = 'VERIFIED'", name="integrity_verified"),
    sa.CheckConstraint(
        "classification = 'development_synthetic'",
        name="classification_development_synthetic",
    ),
    sa.CheckConstraint("verified_at <= created_at", name="verified_before_created"),
    sa.CheckConstraint(
        "((advertised_mime_normalized IS NULL OR intake_detected_mime IS NULL) "
        "AND mime_mismatch IS NULL) OR "
        "(advertised_mime_normalized IS NOT NULL "
        "AND intake_detected_mime IS NOT NULL "
        "AND mime_mismatch = "
        "(advertised_mime_normalized <> intake_detected_mime))",
        name="mime_mismatch_tristate",
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "document_version_id"],
        ["document_versions.tenant_id", "document_versions.id"],
        name="fk_file_objects_version",
        ondelete="RESTRICT",
    ),
)


audit_events = sa.Table(
    "audit_events",
    metadata,
    sa.Column("id", uuid_type, primary_key=True),
    sa.Column("tenant_id", uuid_type, nullable=False),
    sa.Column("event_type", sa.String(64), nullable=False),
    sa.Column("intake_occurrence_id", uuid_type, nullable=False),
    sa.Column("document_envelope_id", uuid_type, nullable=False),
    sa.Column("document_version_id", uuid_type, nullable=False),
    sa.Column("file_object_id", uuid_type, nullable=False),
    sa.Column("actor_id", uuid_type, nullable=False),
    sa.Column("previous_state", sa.String(32), nullable=False),
    sa.Column("resulting_state", sa.String(32), nullable=False),
    sa.Column("correlation_id", uuid_type, nullable=False),
    sa.Column("causation_id", uuid_type, nullable=False),
    sa.Column("source", sa.String(64), nullable=False),
    sa.Column("classification", sa.String(64), nullable=False),
    sa.Column(
        "occurred_at", timestamp_type, nullable=False, server_default=sa.func.now()
    ),
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
        "event_type = 'DOCUMENT_MATERIALIZED'", name="event_type_materialized"
    ),
    sa.CheckConstraint("previous_state = 'MATERIALIZED'", name="previous_materialized"),
    sa.CheckConstraint(
        "resulting_state = 'INSPECTION_PENDING'", name="result_inspection_pending"
    ),
    sa.CheckConstraint(
        "causation_id = intake_occurrence_id", name="causation_occurrence"
    ),
    sa.CheckConstraint("source = 'document_intake'", name="source_document_intake"),
    sa.CheckConstraint(
        "classification = 'development_synthetic'",
        name="classification_development_synthetic",
    ),
    sa.ForeignKeyConstraint(
        ["tenant_id", "intake_occurrence_id"],
        ["document_intake_occurrences.tenant_id", "document_intake_occurrences.id"],
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


IMMUTABLE_TABLES = (
    "document_intake_occurrence_reasons",
    "document_versions",
    "file_objects",
    "audit_events",
)
