"""User model — see Doc 2 §4.1."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False)
    display_name: str = Field(nullable=False, max_length=80)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    last_login_at: datetime | None = Field(default=None, nullable=True)
    onboarding_complete: bool = Field(default=False, nullable=False)
