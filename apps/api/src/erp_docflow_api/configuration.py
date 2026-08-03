"""Runtime configuration loaded explicitly from the process environment."""

from __future__ import annotations

import os
from collections.abc import Mapping

from sqlalchemy.engine import URL

DATABASE_HOST_ENV = "ERP_DOCFLOW_DATABASE_HOST"
DATABASE_PORT_ENV = "ERP_DOCFLOW_DATABASE_PORT"
DATABASE_NAME_ENV = "ERP_DOCFLOW_DATABASE_NAME"
DATABASE_USER_ENV = "ERP_DOCFLOW_DATABASE_USER"
DATABASE_PASSWORD_ENV = "ERP_DOCFLOW_DATABASE_PASSWORD"


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is absent or invalid."""


def _required_component(
    source: Mapping[str, str],
    name: str,
    *,
    preserve_whitespace: bool = False,
) -> str:
    value = source.get(name, "")
    if preserve_whitespace:
        if not value.strip():
            raise ConfigurationError(f"{name} is required")
        return value

    normalized = value.strip()
    if not normalized:
        raise ConfigurationError(f"{name} is required")
    return normalized


def get_database_url(environ: Mapping[str, str] | None = None) -> str:
    """Build the required PostgreSQL SQLAlchemy URL without logging secrets.

    Configuration is resolved only when a database boundary asks for it, so
    importing the API (including its healthcheck) never opens a connection or
    runs migrations as a side effect. ``URL.create`` receives the password as a
    component so reserved URL characters are escaped instead of being parsed as
    delimiters.
    """

    source = os.environ if environ is None else environ
    host = _required_component(source, DATABASE_HOST_ENV)
    port_value = _required_component(source, DATABASE_PORT_ENV)
    database = _required_component(source, DATABASE_NAME_ENV)
    username = _required_component(source, DATABASE_USER_ENV)
    password = _required_component(
        source,
        DATABASE_PASSWORD_ENV,
        preserve_whitespace=True,
    )

    try:
        port = int(port_value)
    except ValueError as error:
        raise ConfigurationError(
            f"{DATABASE_PORT_ENV} must be an integer between 1 and 65535"
        ) from error
    if not 1 <= port <= 65535:
        raise ConfigurationError(
            f"{DATABASE_PORT_ENV} must be an integer between 1 and 65535"
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    ).render_as_string(hide_password=False)
