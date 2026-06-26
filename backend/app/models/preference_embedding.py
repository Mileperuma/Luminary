"""Vector embedding of a user's accumulated preferences, per media type.

Uses pgvector — see backend/db/init/01_enable_pgvector.sql for extension setup.

The vector dimension is 1536 (matches OpenAI's text-embedding-3-small and
Voyage AI voyage-2). If the embedding model changes, write a migration to
re-dimension and re-populate; pgvector won't auto-convert.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.models.base import utcnow
from app.models.preference import MediaType

EMBEDDING_DIM = 1536


class PreferenceEmbedding(SQLModel, table=True):
    __tablename__ = "preference_embeddings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    media_type: MediaType = Field(index=True, nullable=False)
    embedding: list[float] = Field(sa_column=Column(Vector(EMBEDDING_DIM)))
    summary: str = Field(default="", nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
