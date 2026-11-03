from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import ALL_MODELS

IN_MEMORY_DATABASES = {None, "", ":memory:"}


def build_engine(database_url: str) -> Engine:
    """Create an engine, applying the settings SQLite needs to behave like a server database.

    For SQLite this enables foreign keys on every connection, allows use across threads,
    shares a single connection for in-memory databases and creates the database folder.

    Args:
        database_url: SQLAlchemy database URL.

    Returns:
        The configured engine.
    """
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        return create_engine(url)

    options: dict[str, Any] = {"connect_args": {"check_same_thread": False}}
    if url.database in IN_MEMORY_DATABASES:
        options["poolclass"] = StaticPool
    else:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(url, **options)
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory whose objects stay readable after commit."""
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Provide a transactional session that commits on success and rolls back on error."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine: Engine) -> None:
    """Create all tables that do not exist yet."""
    Base.metadata.create_all(engine, tables=[model.__table__ for model in ALL_MODELS])
