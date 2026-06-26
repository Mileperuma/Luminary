"""Shared base columns for all models."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Aware UTC timestamp, used as a default for `created_at` / `updated_at`."""
    return datetime.now(UTC)


class IDModel(SQLModel):
    """Adds a UUID primary key. Inherit this when a table only needs an id."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TimestampMixin(SQLModel):
    """Adds `created_at` and `updated_at` columns."""

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
