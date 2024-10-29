from pydantic_settings import BaseSettings, SettingsConfigDict


class DadataSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dadata_")

    token: str
    secret: str
