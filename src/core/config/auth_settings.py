from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="auth_")

    ACCESS_TOKEN_EXPIRES_IN: int = 900
    REFRESH_TOKEN_EXPIRES_IN: int = 3600
