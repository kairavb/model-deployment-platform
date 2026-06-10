"""Initial database schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _create_enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name, create_type=False)
    enum_type.create(op.get_bind(), checkfirst=True)
    return enum_type


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    model_framework = _create_enum("modelframework", ("sklearn", "onnx", "pytorch"))

    op.create_table(
        "ml_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("framework", model_framework, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_ml_models_user_id_name"),
    )
    op.create_index(op.f("ix_ml_models_user_id"), "ml_models", ["user_id"], unique=False)

    model_version_status = _create_enum("modelversionstatus", ("uploaded", "validated", "invalid"))

    op.create_table(
        "model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("input_schema_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output_schema_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", model_version_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["ml_models.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_id", "version_number", name="uq_model_versions_model_id_version"),
    )
    op.create_index(op.f("ix_model_versions_model_id"), "model_versions", ["model_id"], unique=False)

    deployment_status = _create_enum(
        "deploymentstatus",
        ("pending", "starting", "running", "stopping", "stopped", "failed"),
    )
    health_status = _create_enum("healthstatus", ("unknown", "healthy", "unhealthy"))

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("status", deployment_status, nullable=False),
        sa.Column("container_id", sa.String(length=64), nullable=True),
        sa.Column("host_port", sa.Integer(), nullable=True),
        sa.Column("internal_url", sa.String(length=256), nullable=True),
        sa.Column("health_status", health_status, nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deployments_container_id"), "deployments", ["container_id"], unique=False)
    op.create_index(op.f("ix_deployments_model_version_id"), "deployments", ["model_version_id"], unique=False)
    op.create_index(op.f("ix_deployments_user_id"), "deployments", ["user_id"], unique=False)

    op.create_table(
        "deployment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deployment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deployment_id"], ["deployments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_deployment_events_deployment_id"), "deployment_events", ["deployment_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_deployment_events_deployment_id"), table_name="deployment_events")
    op.drop_table("deployment_events")
    op.drop_index(op.f("ix_deployments_user_id"), table_name="deployments")
    op.drop_index(op.f("ix_deployments_model_version_id"), table_name="deployments")
    op.drop_index(op.f("ix_deployments_container_id"), table_name="deployments")
    op.drop_table("deployments")
    op.drop_index(op.f("ix_model_versions_model_id"), table_name="model_versions")
    op.drop_table("model_versions")
    op.drop_index(op.f("ix_ml_models_user_id"), table_name="ml_models")
    op.drop_table("ml_models")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    postgresql.ENUM(name="healthstatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="deploymentstatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="modelversionstatus").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="modelframework").drop(op.get_bind(), checkfirst=True)
