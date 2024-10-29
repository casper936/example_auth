import re
from datetime import UTC, date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from src.schemas.base import BaseSchemaModel


class UserBaseSchema(BaseSchemaModel):
    username: str = Field(description="логин пользователя")


class ProfileBaseSchema(BaseSchemaModel):
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    patronymic: str | None = Field(None, description="Отчество пользователя")


class RequestUserCreateSchema(BaseSchemaModel):

    email: EmailStr = Field(description="email пользователя")
    password: str = Field(description="пароль пользователя", min_length=8)
    password_check: str = Field(
        description="проверка пароля пользователя", min_length=8
    )

    @field_validator("email", mode="after")
    @classmethod
    def email_lowcase(cls, v: EmailStr):
        return v.lower()

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RequestUserCreateSchema":
        pw1 = self.password
        pw2 = self.password_check
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("пароли не совпадают")
        return self


class UserCreateSchema(BaseSchemaModel):
    email: EmailStr = Field(description="email пользователя")
    username: EmailStr = Field(description="логин пользователя")
    password: str = Field(description="пароль пользователя")


class UserUpdateSchema(BaseSchemaModel):
    password_hash: str | None = Field(None, description="пароль пользователя")
    email: EmailStr | None = Field(None, description="email пользователя")


class UserVerifySchema(BaseSchemaModel):
    email_verified: bool = Field(
        default=True, description="подтверждение email пользователя"
    )
    email_verified_at: datetime = Field(default=datetime.now(UTC))
    is_active: bool = Field(default=True)


class RequestUserProfileCreateSchema(ProfileBaseSchema):
    phone_number: str = Field(description="Номер телефона пользователя")

    birth_day: date | None = Field(None, description="Дата рождения пользователя")
    timezone: str | None = Field(None, description="Таймзона пользователя")

    city_id: UUID = Field(description="ID города")

    @field_validator("phone_number")
    @classmethod
    def convert_phone_number(cls, v: str) -> str:  # pylint: disable=no-self-argument
        return "".join(re.findall(r"\d", v)).strip()

    @field_validator("first_name", "last_name", "patronymic")
    def validate_names(  # pylint: disable=no-self-argument
        cls, v: str | None
    ) -> str | None:
        if v:
            v = v.strip().title()
            result = re.findall(r"[^а-яА-Я-ёЁ ]+", v)
            if not result:
                return v

            raise ValueError(
                "Должно содержать только следующие символы: русские буквы, дефис"
            )
        return None


class UserProfileCreateSchema(RequestUserProfileCreateSchema):
    user_id: UUID = Field(description="ID пользователя")


class UserProfileUpdateSchema(ProfileBaseSchema):
    first_name: str | None = Field(None, description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    patronymic: str | None = Field(None, description="Отчество пользователя")
    phone_number: str | None = Field(None, description="Номер телефона пользователя")
    birth_day: date | None = Field(None, description="Дата рождения пользователя")
    timezone: str | None = Field(None, description="Таймзона пользователя")

    city_id: UUID | None = Field(None, description="ID города")


class UserProfileInDB(BaseSchemaModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(description="ФИО пользователя")


class UserProfileSchema(UserProfileInDB):
    pass


class UserInDB(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class UserSchema(UserInDB):
    email: EmailStr


class UserProfileFullSchema(UserProfileInDB):
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    patronymic: str | None = Field(None, description="Отчество пользователя")

    phone_number: str = Field(description="Номер телефона пользователя")
    birth_day: date | None = Field(None, description="Дата рождения пользователя")

    city_id: UUID = Field(description="ID города")
    timezone: str | None = Field(None, description="Таймзона пользователя")

    user: UserSchema


class UserFullSchema(UserSchema):
    profile: UserProfileFullSchema | None = {}


class CreateUserSingInSchema(BaseModel):
    user_id: UUID
    user_agent: str
    user_platform: str

    user_device_type: str
