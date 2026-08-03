"""Alembic lifecycle and physical-schema contract tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine

from erp_docflow_api.configuration import DATABASE_NAME_ENV

pytestmark = pytest.mark.postgres

API_ROOT = Path(__file__).resolve().parents[3]


def test_single_head_and_schema_has_no_binary_column(
    postgres_engine: Engine,
) -> None:
    config = Config(str(API_ROOT / "alembic.ini"))
    command.current(config, check_heads=True)
    command.check(config)

    with postgres_engine.connect() as connection:
        rows = connection.execute(
            sa.text(
                "SELECT table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema = current_schema() "
                "AND table_name IN ('document_intake_occurrences', "
                "'document_envelopes', 'document_versions', 'file_objects', "
                "'audit_events')"
            )
        ).mappings()
        columns = tuple(rows)
    assert columns
    assert all(row["data_type"] != "bytea" for row in columns)


def test_disposable_database_downgrade_upgrade_cycle(
    postgres_database_url: str,
) -> None:
    assert "erp_docflow_test_" in postgres_database_url
    config = Config(str(API_ROOT / "alembic.ini"))
    assert os.environ[DATABASE_NAME_ENV].startswith("erp_docflow_test_")

    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.current(config, check_heads=True)
