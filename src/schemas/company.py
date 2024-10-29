import re
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from src.schemas.base import AuditSchema, BaseSchemaModel


class CompanyBaseSchema(BaseSchemaModel):
    name: str = Field(description="Название компании")


class RequestCompanyCreateSchema(CompanyBaseSchema):
    inn: str = Field(description="ИНН компании")

    description: str | None = Field(None, description="Описание компании")
    phone_number: str | None = Field(None, description="Номер телефона компании")
    url: str | None = Field(None, description="Ссылка на сайт компании")

    @field_validator("phone_number")
    @classmethod
    def convert_phone_number(cls, v: str) -> str:  # pylint: disable=no-self-argument
        return "".join(re.findall(r"\d", v)).strip()


class RequestCompanyUpdateSchema(BaseSchemaModel):
    name: str | None = Field(None, description="Название компании")
    description: str | None = Field(None, description="Описание компании")
    phone_number: str | None = Field(None, description="Номер телефона компании")
    url: str | None = Field(None, description="Ссылка на сайт компании")

    @field_validator("phone_number")
    @classmethod
    def convert_phone_number(cls, v: str) -> str:  # pylint: disable=no-self-argument
        return "".join(re.findall(r"\d", v)).strip()


class CompanyCreateSchema(RequestCompanyCreateSchema, AuditSchema):
    pass


class CompanyUpdateSchema(RequestCompanyUpdateSchema):
    updated_by: str


class CommpanyInDB(CompanyBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class CompanySchema(CommpanyInDB):
    phone_number: str | None = Field(None, description="Номер телефона компании")
    url: str | None = Field(None, description="Ссылка на сайт компании")


class CompanyFullSchema(CompanySchema):
    inn: str = Field(description="ИНН компании")
    description: str | None = Field(None, description="Описание компании")


class CompanyBranchBaseSchema(BaseSchemaModel):
    name: str = Field(description="Название филиала компании")
    address: str = Field(description="Адрес филиала компании")


class RequestCompanyBranchCreateSchema(CompanyBranchBaseSchema, AuditSchema):
    city_id: UUID = Field(description="ID города где расположен филиал")
    company_id: UUID = Field(description="ID компании к которой принадлежит филиал")

    description: str | None = Field(None, description="Описание филиала компании")
    phone_number: str | None = Field(
        None, description="Номер телефона филиала компании"
    )
    timezone: str | None = Field(None, description="Таймзона филиала компании")


class RequestCompanyBranchUpdateSchema(BaseSchemaModel):
    description: str | None = Field(None, description="Описание филиала компании")
    phone_number: str | None = Field(
        None, description="Номер телефона филиала компании"
    )
    timezone: str | None = Field(None, description="Таймзона филиала компании")
    is_active: bool = Field(default=True, description="Признак активности филиала")


class CompanyBranchCreateSchema(RequestCompanyBranchCreateSchema, AuditSchema):
    pass


class CompanyBranchUpdateSchema(RequestCompanyBranchUpdateSchema):
    updated_by: str


class CompanyBranchInDB(CompanyBranchBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class CompanyBranchSchema(CompanyBranchInDB):
    phone_number: str | None = Field(
        None, description="Номер телефона филиала компании"
    )


class CompanyBranchFullSchema(CompanyBranchSchema):
    city: str
