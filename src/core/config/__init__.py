from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.config.auth_jwt_settings import AuthJWTSettings
from src.core.config.auth_settings import AuthSettings
from src.core.config.dadata_settings import DadataSettings
from src.core.config.email_settings import EmailSettings
from src.core.config.pg_settings import DBSettings
from src.core.config.redis_settings import RedisSettings


class BaseSettingsConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


class Settings(BaseSettingsConfig):
    app_name: str
    app_version: str
    app_environment: str = Field(default="local")
    debug: bool = Field(default=False)
    app_origins: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    auth: AuthSettings = Field(default_factory=AuthSettings)
    auth_jwt: AuthJWTSettings = Field(default_factory=AuthJWTSettings)
    dadata: DadataSettings = Field(default_factory=DadataSettings)
    db: DBSettings = Field(default_factory=DBSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)


settings = Settings()
