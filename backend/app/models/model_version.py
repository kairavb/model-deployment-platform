import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class ModelVersionStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    INVALID = "invalid"


class ModelVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint("model_id", "version_number", name="uq_model_versions_model_id_version"),
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ml_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    input_schema_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_schema_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ModelVersionStatus] = mapped_column(
        Enum(ModelVersionStatus),
        nullable=False,
        default=ModelVersionStatus.UPLOADED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    model: Mapped["MLModel"] = relationship(back_populates="versions")
    deployments: Mapped[list["Deployment"]] = relationship(back_populates="model_version")


from app.models.deployment import Deployment  # noqa: E402
from app.models.model import MLModel  # noqa: E402
