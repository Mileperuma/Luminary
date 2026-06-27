"""Pydantic schemas for preferences."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.preference import MediaType, PreferenceSource


class PreferencePublic(BaseModel):
    id: UUID
    user_id: UUID
    media_type: MediaType
    key: str
    value: str
    weight: float
    source: PreferenceSource
    updated_at: datetime


class PreferenceCreate(BaseModel):
    media_type: MediaType
    key: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=200)
    weight: float = Field(default=0.5, ge=-1.0, le=1.0)


class PreferenceUpdate(BaseModel):
    value: str | None = Field(default=None, min_length=1, max_length=200)
    weight: float | None = Field(default=None, ge=-1.0, le=1.0)


class PreferencesBulkCreate(BaseModel):
    preferences: list[PreferenceCreate]
