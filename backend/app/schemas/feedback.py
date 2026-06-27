"""Pydantic schemas for the feedback endpoint."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.recommendation import FeedbackKind


class FeedbackCreate(BaseModel):
    recommendation_id: UUID
    kind: FeedbackKind


class FeedbackPublic(BaseModel):
    id: UUID
    recommendation_id: UUID
    kind: FeedbackKind
    created_at: datetime
    preference_delta: int  # how many preference weights moved as a result
