import typing
import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_mixins import AuditMixin, Base, BaseMixin, TimestampMixin
from src.models.user import users_company_table

association_company_table = Table(
    "company_company_types",
    Base.metadata,
    Column("company_type_id", ForeignKey("company_types.id"), primary_key=True),
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
)

if typing.TYPE_CHECKING:
    from src.models.kladr import City
    from src.models.user import User


class CompanyType(Base, BaseMixin):

    __tablename__ = "company_types"

    name: Mapped[str] = mapped_column(String)
    label: Mapped[str] = mapped_column(String)

    companies: Mapped[list["Company"]] = relationship(
        secondary=association_company_table, back_populates="types"
    )


class Company(Base, BaseMixin, TimestampMixin, AuditMixin):
    """
    Модель компании

    Связи:
        one-to-many: User, CompanyBranch
        many-to-many: CompanyType
    """

    name: Mapped[str] = mapped_column(String, index=True)
    inn: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None]
    phone_number: Mapped[str | None]
    url: Mapped[str | None]

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company_branch: Mapped["CompanyBranch"] = relationship(
        back_populates="company", order_by="asc(CompanyBranch.name)"
    )
    types: Mapped[list[CompanyType]] = relationship(
        secondary=association_company_table, back_populates="companies"
    )
    users: Mapped[list["User"]] = relationship(
        secondary=users_company_table, back_populates="companies"
    )


class CompanyBranch(Base, BaseMixin, TimestampMixin, AuditMixin):
    """
    Модель филиала компании

    """

    __tablename__ = "company_branch"

    name: Mapped[str] = mapped_column(String, index=True)

    description: Mapped[str | None]
    phone_number: Mapped[str | None]
    address: Mapped[str] = mapped_column(String)

    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id"))
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company: Mapped["Company"] = relationship(back_populates="company_branch")
    city: Mapped["City"] = relationship(backref="company_branch", lazy="joined")
