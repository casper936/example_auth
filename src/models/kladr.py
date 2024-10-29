import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_mixins import Base, BaseMixin


class City(Base, BaseMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    timezone: Mapped[str | None]
    fias_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
    )
    kladr_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=True,
    )
