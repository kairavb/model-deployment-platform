from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    models: Mapped[list["MLModel"]] = relationship(back_populates="owner")
    deployments: Mapped[list["Deployment"]] = relationship(back_populates="owner")


from app.models.deployment import Deployment  # noqa: E402
from app.models.model import MLModel  # noqa: E402
