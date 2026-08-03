"""Synchronous PostgreSQL engine, session factory, and Unit of Work."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from erp_docflow_api.persistence.postgresql.repositories import (
    MaterializationRepository,
)

SessionFactory = sessionmaker[Session]


def create_postgresql_engine(database_url: str, *, echo: bool = False) -> Engine:
    """Create an Engine without connecting or mutating the database."""

    url = make_url(database_url)
    if url.drivername != "postgresql+psycopg":
        raise ValueError("database_url must use the postgresql+psycopg dialect")
    return create_engine(
        url,
        echo=echo,
        pool_pre_ping=True,
        future=True,
    )


def create_session_factory(engine: Engine) -> SessionFactory:
    """Build explicit, non-autocommit sessions for one PostgreSQL Engine."""

    if engine.dialect.name != "postgresql":
        raise ValueError("PostgreSQL is required; SQLite fallback is not supported")
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class PostgresqlUnitOfWork:
    """Own one transaction and expose repositories bound to its Session.

    Calling :meth:`commit` is explicit.  Leaving the context without committing
    rolls the transaction back, which prevents accidental partial publication.
    """

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None
        self.materializations: MaterializationRepository | None = None
        self._committed = False

    def __enter__(self) -> PostgresqlUnitOfWork:
        self.session = self._session_factory()
        self.materializations = MaterializationRepository(self.session)
        self._committed = False
        return self

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work has not been entered")
        self.session.commit()
        self._committed = True

    def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work has not been entered")
        self.session.rollback()
        self._committed = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            return
        try:
            if exc_type is not None or not self._committed:
                self.session.rollback()
        finally:
            self.session.close()
            self.session = None
            self.materializations = None
