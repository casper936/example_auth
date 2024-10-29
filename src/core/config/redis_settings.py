from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    host: str
    port: str
    username: str = Field(default="default")
    password: str
    cache_dsn: str | None = None

    CACHE_EXPIRE_IN_SECONDS: int = 300

    def __init__(self, **data) -> None:  # type: ignore
        super(RedisSettings, self).__init__(**data)
        self.cache_dsn = (
            f"redis://{self.username}:{self.password}@{self.host}:{self.port}/0"
        )

    model_config = SettingsConfigDict(env_prefix="redis_")
