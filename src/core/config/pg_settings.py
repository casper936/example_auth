from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class DBSettings(BaseSettings):
    pg_dsn: str
    db_schema: str = Field(default="catalog")

    model_config = SettingsConfigDict(env_prefix="database_")
