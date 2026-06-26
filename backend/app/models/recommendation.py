"""Recommendation + feedback models."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.base import utcnow
from app.models.preference import MediaType


class FeedbackKind(StrEnum):
    LOVE = "love"
    DISLIKE = "dislike"
    SAVE = "save"
    SKIP = "skip"   # "show me another"


# Portable JSON column — generic JSON on SQLite (used by tests), JSONB on PostgreSQL.
# JSONB gives indexing + jsonpath in production; JSON keeps the in-memory test DB happy.
_SimilarItemsCol = JSON().with_variant(JSONB(), "postgresql")


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    media_type: MediaType = Field(index=True, nullable=False)
    external_id: str = Field(nullable=False, max_length=120)
    title: str = Field(nullable=False, max_length=250)
    image_url: str | None = Field(default=None, max_length=500)
    trailer_url: str | None = Field(default=None, max_length=500)
    description: str = Field(default="", nullable=False)
    similar_items: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(_SimilarItemsCol, nullable=False, server_default="[]"),
    )
    created_at: datetime = Field(default_factory=utcnow, index=True, nullable=False)


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    recommendation_id: UUID = Field(foreign_key="recommendations.id", index=True, nullable=False)
    kind: FeedbackKind = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
