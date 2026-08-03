from __future__ import annotations

import pytest
from sqlalchemy.engine import make_url

from erp_docflow_api.configuration import (
    DATABASE_HOST_ENV,
    DATABASE_NAME_ENV,
    DATABASE_PASSWORD_ENV,
    DATABASE_PORT_ENV,
    DATABASE_USER_ENV,
    ConfigurationError,
    get_database_url,
)

VALID_ENV = {
    DATABASE_HOST_ENV: "postgres",
    DATABASE_PORT_ENV: "5432",
    DATABASE_NAME_ENV: "erp_docflow_test",
    DATABASE_USER_ENV: "erp_docflow",
    DATABASE_PASSWORD_ENV: "synthetic:p@ss/word",
}


@pytest.mark.parametrize("missing", sorted(VALID_ENV))
def test_database_configuration_is_fail_closed(missing: str) -> None:
    environment = VALID_ENV | {missing: ""}

    with pytest.raises(ConfigurationError, match=missing):
        get_database_url(environment)


@pytest.mark.parametrize("port", ["not-a-port", "0", "65536"])
def test_database_port_must_be_valid(port: str) -> None:
    environment = VALID_ENV | {DATABASE_PORT_ENV: port}

    with pytest.raises(ConfigurationError, match=DATABASE_PORT_ENV):
        get_database_url(environment)


def test_database_password_is_encoded_as_a_url_component() -> None:
    url = make_url(get_database_url(VALID_ENV))

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "postgres"
    assert url.database == "erp_docflow_test"
    assert url.username == "erp_docflow"
    assert url.password == "synthetic:p@ss/word"
