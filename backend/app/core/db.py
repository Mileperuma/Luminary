"""Database engine and session management.

Synchronous SQLAlchemy/SQLModel for the MVP — keeps the stack small and the
test setup simple. If async becomes a measurable bottleneck in Phase 2 we can
swap in `AsyncSession`; the call sites already use FastAPI dependency injection
so the change would be local.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session and closes it after."""
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """Create all tables — used by tests and the first dev boot.

    Production uses Alembic migrations (see backend/alembic/), not this helper.
    """
    SQLModel.metadata.create_all(engine)
