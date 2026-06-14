import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

_engine = None
_session_factory = None


def _get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(f"Environment variable {name} is required")

    return value


def get_database_url() -> str:
    host = _get_required_env("POSTGRES_HOST")
    port = _get_required_env("POSTGRES_PORT")
    database = _get_required_env("POSTGRES_DB")
    user = _get_required_env("POSTGRES_USER")
    password = _get_required_env("POSTGRES_PASSWORD")

    return (
        "postgresql+psycopg2://"
        f"{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{database}"
    )


def get_engine():
    global _engine

    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
        )

    return _engine


def get_session_factory():
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )

    return _session_factory


def get_db():
    session_factory = get_session_factory()
    db = session_factory()

    try:
        yield db
    finally:
        db.close()