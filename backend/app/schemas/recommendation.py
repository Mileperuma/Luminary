"""Pydantic schemas for recommendation endpoints."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.preference import MediaType


class RecommendationRequest(BaseModel):
    media_type: MediaType
    mood: str | None = Field(default=None, max_length=40)


class CatalogueItemPublic(BaseModel):
    media_type: MediaType
    external_id: str
    title: str
    description: str = ""
    image_url: str | None = None
    trailer_url: str | None = None
    keywords: list[str] = []


class RecommendationPublic(BaseModel):
    id: UUID
    media_type: MediaType
    external_id: str
    title: str
    image_url: str | None
    trailer_url: str | None
    description: str
    similar_items: list[dict[str, Any]]
    created_at: datetime
