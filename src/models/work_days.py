import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_mixins import Base, BaseMixin

if TYPE_CHECKING:
    from src.models.company import CompanyBranch


class WorkDays(Base, BaseMixin):
    __tablename__ = "work_days"

    __table_args__ = (
        UniqueConstraint("company_branch", name="_workdays_company_branch_uc"),
    )

    weekdays: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(ARRAY(Integer)), nullable=False
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    company_branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("company_branch.id")
    )
    company_branch: Mapped["CompanyBranch"] = relationship(backref="work_days")
