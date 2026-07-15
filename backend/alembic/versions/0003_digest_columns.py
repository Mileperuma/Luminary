"""add digest_opt_in + last_digest_sent_at on users

Revision ID: 0003_digest_columns
Revises: 0002_pgvector_index
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_digest_columns"
down_revision: str | None = "0002_pgvector_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("digest_opt_in", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "users",
        sa.Column("last_digest_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "last_digest_sent_at")
    op.drop_column("users", "digest_opt_in")
