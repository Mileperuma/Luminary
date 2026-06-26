"""initial schema — all seven MVP tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # pgvector extension — idempotent
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("email", sqlmodel.AutoString(length=255), nullable=False),
        sa.Column("password_hash", sqlmodel.AutoString(), nullable=False),
        sa.Column("display_name", sqlmodel.AutoString(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "preferences",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("key", sqlmodel.AutoString(length=80), nullable=False),
        sa.Column("value", sqlmodel.AutoString(length=200), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_preferences_user_id", "preferences", ["user_id"])
    op.create_index("ix_preferences_media_type", "preferences", ["media_type"])

    op.create_table(
        "preference_embeddings",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_preference_embeddings_user_id", "preference_embeddings", ["user_id"])
    op.create_index("ix_preference_embeddings_media_type", "preference_embeddings", ["media_type"])

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("session_type", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("external_id", sqlmodel.AutoString(length=120), nullable=False),
        sa.Column("title", sqlmodel.AutoString(length=250), nullable=False),
        sa.Column("image_url", sqlmodel.AutoString(length=500), nullable=True),
        sa.Column("trailer_url", sqlmodel.AutoString(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "similar_items",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])
    op.create_index("ix_recommendations_media_type", "recommendations", ["media_type"])
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"])

    op.create_table(
        "feedback",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("recommendation_id", sa.UUID(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_recommendation_id", "feedback", ["recommendation_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("recommendations")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("preference_embeddings")
    op.drop_table("preferences")
    op.drop_table("users")
