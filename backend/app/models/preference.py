"""Preference model — typed key-value taste tag per user per media type."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class MediaType(StrEnum):
    BOOK = "book"
    MOVIE = "movie"
    ARTICLE = "article"


class PreferenceSource(StrEnum):
    CHAT = "chat"           # captured during onboarding conversation
    EXPLICIT = "explicit"   # user-edited in settings
    IMPLICIT = "implicit"   # inferred from feedback


class Preference(SQLModel, table=True):
    __tablename__ = "preferences"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    media_type: MediaType = Field(index=True, nullable=False)
    key: str = Field(nullable=False, max_length=80)
    value: str = Field(nullable=False, max_length=200)
    weight: float = Field(default=0.5, nullable=False)  # -1.0 .. +1.0
    source: PreferenceSource = Field(default=PreferenceSource.CHAT, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
