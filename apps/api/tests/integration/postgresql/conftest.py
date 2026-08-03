"""Disposable real-PostgreSQL fixtures; SQLite and create_all are forbidden."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from erp_docflow_api.configuration import DATABASE_NAME_ENV, get_database_url
from erp_docflow_api.persistence.postgresql.session import (
    create_postgresql_engine,
    create_session_factory,
)

API_ROOT = Path(__file__).resolve().parents[3]
TABLES = (
    "audit_events",
    "file_objects",
    "document_versions",
    "document_envelopes",
    "document_intake_occurrence_reasons",
    "document_intake_occurrences",
)


@pytest.fixture(scope="session")
def postgres_database_url() -> Iterator[str]:
    try:
        base_url = make_url(get_database_url())
    except RuntimeError as error:
        pytest.fail(
            "explicit ERP_DOCFLOW_DATABASE_* components are required for "
            f"PostgreSQL integration tests: {error}"
        )
    if base_url.drivername != "postgresql+psycopg":
        pytest.fail("database configuration must use postgresql+psycopg")

    database_name = f"erp_docflow_test_{uuid4().hex}"
    test_url = base_url.set(database=database_name)
    admin_engine = create_postgresql_engine(
        base_url.set(database="postgres").render_as_string(hide_password=False)
    ).execution_options(isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.exec_driver_sql(f'CREATE DATABASE "{database_name}"')

    previous_database_name = os.environ.get(DATABASE_NAME_ENV)
    os.environ[DATABASE_NAME_ENV] = database_name
    config = Config(str(API_ROOT / "alembic.ini"))
    try:
        command.upgrade(config, "head")
        yield test_url.render_as_string(hide_password=False)
    finally:
        if previous_database_name is None:
            os.environ.pop(DATABASE_NAME_ENV, None)
        else:
            os.environ[DATABASE_NAME_ENV] = previous_database_name
        with admin_engine.connect() as connection:
            connection.exec_driver_sql(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            connection.exec_driver_sql(f'DROP DATABASE "{database_name}"')
        admin_engine.dispose()


@pytest.fixture(scope="session")
def postgres_engine(postgres_database_url: str) -> Iterator[Engine]:
    engine = create_postgresql_engine(postgres_database_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def postgres_session_factory(
    postgres_engine: Engine,
) -> sessionmaker[Session]:
    return create_session_factory(postgres_engine)


@pytest.fixture(autouse=True)
def clean_materialization_tables(postgres_engine: Engine) -> Iterator[None]:
    yield
    with postgres_engine.begin() as connection:
        existing = sa.inspect(connection).get_table_names()
        tables = [table for table in TABLES if table in existing]
        if tables:
            connection.exec_driver_sql(f"TRUNCATE {', '.join(tables)} CASCADE")
