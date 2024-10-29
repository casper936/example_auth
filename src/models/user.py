import typing
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.models.base_mixins import Base, BaseMixin, TimestampMixin
from src.utils.crypto import make_random_password, pbkdf2, verify

if typing.TYPE_CHECKING:
    from src.models.company import Company
    from src.models.kladr import City


users_company_table = Table(
    "users_companies",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
)


class User(Base, BaseMixin, TimestampMixin):
    """
    Модель содержит информацию о пользователе
    Связь: one-to-one с моделью Profile
    """

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    profile: Mapped["Profile"] = relationship(back_populates="user", lazy="joined")
    companies: Mapped["Company"] = relationship(
        secondary=users_company_table, back_populates="users"
    )

    def set_password(self, password: str) -> None:
        """
        Sets users password using pbkdf2
        """

        self.password_hash = pbkdf2(password=password)

    def set_random_password(self) -> str:
        """
        Set random password
        """
        password = make_random_password()
        self.password_hash = pbkdf2(password)

        return password

    def verify_password(self, password: str) -> bool:
        """
        Verify users password
        """
        if self.password_hash is None:
            return False
        return verify(password, self.password_hash)

    @hybrid_property
    def is_authenticated(self) -> bool:
        return True

    def __repr__(self):
        return f"<User {self.username}>"


class UserSingInMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_agent: Mapped[str] = mapped_column(String)
    user_platform: Mapped[str] = mapped_column(String)
    user_device_type: Mapped[str] = mapped_column(String, primary_key=True)

    logined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
    )


class UserSingIn(UserSingInMixin, Base):
    """
    Модель истории авторизаций пользователя который хранит следующую информацию

    Params:
        user_id: ID пользователя (связь один-ко многим с моделью User)
        logined_by: дата авторизации
        user_agent: устройство, с которого была выполнена аутентификация.
        user_device_type: тип устройства (web, mobile, api)
    """

    __tablename__ = "users_sign_in"

    __table_args__ = {"postgresql_partition_by": "LIST (user_device_type)"}


class UserSingInAPI(UserSingInMixin, Base):
    __tablename__ = "user_sign_in_api"


class UserSingInMobile(UserSingInMixin, Base):
    __tablename__ = "user_sign_in_mobile"


class UserSingInWEB(UserSingInMixin, Base):
    __tablename__ = "user_sign_in_web"


class UserSocialAccount(Base, BaseMixin):
    """
    Модель хранит информацию об аутентификации через социальные сервисы
    """

    __tablename__ = "user_social_account"
    __table_args__ = (
        UniqueConstraint("social_id", "social_name", name="_social_id_social_name_uc"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    social_id: Mapped[str] = mapped_column(String)
    social_name: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<UserSocialAccount {self.social_name}:{self.user_id}>"


class Profile(Base, BaseMixin, TimestampMixin):
    """
    Профиль пользователя
    Связь: one-to-one с моделью User
    """

    __table_args__ = (UniqueConstraint("user_id", name="_profile_user_id_uc"),)

    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    patronymic: Mapped[str | None]
    birth_day: Mapped[date | None]
    timezone: Mapped[str | None]

    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="profile", lazy="joined")
    city: Mapped["City"] = relationship(backref="profile", lazy="joined")

    @hybrid_property
    def full_name(self) -> str:
        fullname = f"{self.last_name} {self.first_name} {self.patronymic}"

        return fullname.replace("None", "").strip().title()


@event.listens_for(UserSingIn.__table__, "after_create")
def create_partition(target, connection, **kwargs) -> None:

    # pylint: disable=no-member
    connection.execute(
        f"""CREATE TABLE IF NOT EXISTS "{settings.db.db_schema}.user_sign_in_api" \
            PARTITION OF "{settings.db.db_schema}.users_sign_in" FOR VALUES IN ('api')"""
    )
    connection.execute(
        f"""CREATE TABLE IF NOT EXISTS "{settings.db.db_schema}.user_sign_in_mobile" \
            PARTITION OF "{settings.db.db_schema}.users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        f"""CREATE TABLE IF NOT EXISTS "{settings.db.db_schema}.user_sign_in_web" \
            PARTITION OF "{settings.db.db_schema}.users_sign_in" FOR VALUES IN ('web')"""
    )
