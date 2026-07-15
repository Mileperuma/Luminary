"""pgvector ivfflat index on preference_embeddings

Revision ID: 0002_pgvector_index
Revises: 0001_initial_schema
Create Date: 2026-08-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_pgvector_index"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ivfflat index for approximate nearest-neighbour on the cosine metric.
    # `lists = 100` is a reasonable default for our scale (< 100k rows).
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_preference_embeddings_embedding_cosine "
        "ON preference_embeddings USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_preference_embeddings_embedding_cosine")
