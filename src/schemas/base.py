from typing import Any

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchemaModel(BaseModel):

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel
        ),
        populate_by_name=True,
    )


class AuditSchema(BaseModel):
    created_by: str
    updated_by: str | None = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.updated_by = self.created_by
