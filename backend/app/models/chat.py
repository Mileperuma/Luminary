"""Chat session + chat message models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSessionType(StrEnum):
    ONBOARDING = "onboarding"
    GENERAL = "general"


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    session_type: ChatSessionType = Field(default=ChatSessionType.GENERAL, nullable=False)
    started_at: datetime = Field(default_factory=utcnow, nullable=False)
    ended_at: datetime | None = Field(default=None, nullable=True)
    summary: str = Field(default="", nullable=False)


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="chat_sessions.id", index=True, nullable=False)
    role: ChatRole = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
