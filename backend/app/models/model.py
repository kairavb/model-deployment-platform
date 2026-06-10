import enum
import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, pg_enum


class ModelFramework(str, enum.Enum):
    SKLEARN = "sklearn"
    ONNX = "onnx"
    PYTORCH = "pytorch"


class MLModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ml_models"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_ml_models_user_id_name"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    framework: Mapped[ModelFramework] = mapped_column(
        pg_enum(ModelFramework, "modelframework"),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="models")
    versions: Mapped[list["ModelVersion"]] = relationship(back_populates="model")


from app.models.model_version import ModelVersion  # noqa: E402
from app.models.user import User  # noqa: E402
