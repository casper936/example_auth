import uuid
from datetime import datetime, timezone
from typing import Self

from sqlalchemy import TIMESTAMP, MetaData, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings

# Default naming convention for all indexes and constraints
# See why this is important and how it would save your time:
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=convention,
        schema=settings.db.db_schema,  # pylint: disable=no-member
    )


class BaseMixin:
    """
    Базовая модель. Добавляет во всех наследников поле id и атрибут
    __tablename__ который заполняется автоматически.
    Имя таблицы берется из названия класса, переводится в нижний регистр и преобразуется в множественное число.
    """

    @declared_attr
    def __tablename__(cls) -> Self:  # pylint: disable=no-self-argument
        if f"{cls.__name__.lower()}"[-1] == "y":  # type: ignore
            new_name = f"{cls.__name__.lower()}"[:-1]  # type: ignore
            return f"{new_name}ies"  # type: ignore
        return f"{cls.__name__.lower()}s"  # type: ignore

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class TimestampMixin:
    """
    Mixin который добавляет в другие модели поля:
    created_at - дата создания
    updated_at - дата последнего обновления
    Поля заполняются автоматически.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )


class AuditMixin:
    """
    Mixin который добавляет в другие модели поля:
    created_by - кем создано
    updated_by - кем обновлено
    """

    created_by: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by: Mapped[str] = mapped_column(Text, nullable=False)
