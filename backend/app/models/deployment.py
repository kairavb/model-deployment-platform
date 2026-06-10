import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, pg_enum


class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class HealthStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class Deployment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deployments"

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[DeploymentStatus] = mapped_column(
        pg_enum(DeploymentStatus, "deploymentstatus"),
        nullable=False,
        default=DeploymentStatus.PENDING,
    )
    container_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    host_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    internal_url: Mapped[str | None] = mapped_column(String(256), nullable=True)
    health_status: Mapped[HealthStatus] = mapped_column(
        pg_enum(HealthStatus, "healthstatus"),
        nullable=False,
        default=HealthStatus.UNKNOWN,
    )
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    model_version: Mapped["ModelVersion"] = relationship(back_populates="deployments")
    owner: Mapped["User"] = relationship(back_populates="deployments")
    events: Mapped[list["DeploymentEvent"]] = relationship(back_populates="deployment")
    inference_logs: Mapped[list["InferenceLog"]] = relationship(back_populates="deployment")


class DeploymentEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "deployment_events"

    deployment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deployments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deployment: Mapped[Deployment] = relationship(back_populates="events")


from app.models.inference_log import InferenceLog  # noqa: E402
from app.models.model_version import ModelVersion  # noqa: E402
from app.models.user import User  # noqa: E402
