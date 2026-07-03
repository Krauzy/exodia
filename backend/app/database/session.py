from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_columns = {
        "targets": "user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE",
        "scans": "user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE",
        "reports": "user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE",
    }
    with engine.begin() as connection:
        for table, definition in required_columns.items():
            if table not in existing_tables:
                continue
            columns = {column["name"] for column in inspector.get_columns(table)}
            if "user_id" not in columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {definition}"))
