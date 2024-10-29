from pydantic import AnyHttpUrl, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="email_")

    host: str
    port: int

    username: str
    password: str
    email: EmailStr
    sender: str = Field(default="pawmate.ru")

    verification_code_url: AnyHttpUrl
    verification_code_expire_sec: int = 900
