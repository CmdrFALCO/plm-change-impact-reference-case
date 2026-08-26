from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_PATH = Path("plm_ref.db")


def sqlite_url(database_path: str | Path = DEFAULT_DATABASE_PATH) -> URL:
    path = Path(database_path)
    return URL.create("sqlite+pysqlite", database=str(path))


def install_sqlite_foreign_key_hook(engine: Engine) -> None:
    """Ensure every SQLite DB-API connection enforces foreign keys."""

    if engine.dialect.name != "sqlite":
        return

    if getattr(engine, "_plm_ref_fk_hook_installed", False):
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    setattr(engine, "_plm_ref_fk_hook_installed", True)


def create_sqlite_engine(database_path: str | Path = DEFAULT_DATABASE_PATH) -> Engine:
    engine = create_engine(sqlite_url(database_path), future=True)
    install_sqlite_foreign_key_hook(engine)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
