"""Pydantic schemas for chat endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.chat import ChatSessionType


class StartChatRequest(BaseModel):
    session_type: ChatSessionType = ChatSessionType.GENERAL


class StartChatResponse(BaseModel):
    session_id: UUID
    opening_message: str


class ChatMessageRequest(BaseModel):
    session_id: UUID
    content: str = Field(min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    session_id: UUID
    assistant_message: str
    finished: bool
    captured_preferences: int = 0
