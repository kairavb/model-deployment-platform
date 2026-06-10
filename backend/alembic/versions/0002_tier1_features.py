"""Tier 1 features: API keys and inference logs.

Revision ID: 0002_tier1
Revises: 0001_initial
Create Date: 2026-06-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_tier1"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key_prefix", sa.String(length=12), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index(op.f("ix_api_keys_user_id"), "api_keys", ["user_id"], unique=False)

    op.create_table(
        "inference_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deployment_id"], ["deployments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inference_logs_created_at"), "inference_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_inference_logs_deployment_id"), "inference_logs", ["deployment_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inference_logs_deployment_id"), table_name="inference_logs")
    op.drop_index(op.f("ix_inference_logs_created_at"), table_name="inference_logs")
    op.drop_table("inference_logs")
    op.drop_index(op.f("ix_api_keys_user_id"), table_name="api_keys")
    op.drop_table("api_keys")
