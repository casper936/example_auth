import pickle
from functools import lru_cache
from typing import Any, TypeVar, Union

import structlog
from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from src.db.redis import get_redis

SetSchemaType = TypeVar("SetSchemaType", bound=BaseModel)
logger = structlog.get_logger(__name__)


class Cache:
    def __init__(self, db: Redis) -> None:  # type: ignore
        self.db = db

    async def get(self, *, key: str) -> Any:
        """Return the value at `key` name, or `None` if the key doesn't exist"""

        return await self.db.get(key)

    async def set(self, *, key: str, value: Union[str, bytes]) -> None:
        try:
            await self.db.set(key, value)
        except Exception as error:
            logger.error(f"Не возможно записать в Redis: {error}")
            raise ValueError("Не возможно создать запись")

    async def hset(
        self,
        key: str | None = None,
        value: bytes | str | None = None,
        mapping: dict[str, Any] | None = None,
        items: list[dict[str, Any]] | None = None,
        *,
        name: str,
    ) -> None:
        """Set ``key`` to ``value`` within hash ``name``,
        ``mapping`` accepts a dict of key/value pairs that will be
        added to hash ``name``.
        """
        try:
            await self.db.hset(
                name=name,
                key=key,  # type: ignore
                value=value,  # type: ignore
                mapping=mapping,  # type: ignore
                items=items,
            )
        except Exception as error:
            logger.error(f"Не возможно записать в Redis: {error}")
            raise ValueError("Не возможно создать запись")

        logger.info("HSET to Redis is done", name=f"{name}")

    async def hget(self, *, name: str, key: str) -> Any:
        """Return the value of `key` within the hash `name`"""

        unpickle_data = await self.db.hget(name=name, key=key)
        if unpickle_data:
            if isinstance(unpickle_data, bytes):
                return pickle.loads(unpickle_data)
            return unpickle_data
        return None

    async def hgetall(self, *, name: str) -> dict[str, Any]:
        return await self.db.hgetall(name)

    async def hkeys(self, *, name: str) -> Any:
        """Return the list of keys within hash ``name``"""

        return await self.db.hkeys(name=name)

    async def hdel(self, name: str, *keys: Any) -> None:
        await self.db.hdel(name, *keys)

    async def keys(self, *, pattern: str = "*") -> list[str]:
        return await self.db.keys(pattern=pattern)

    async def delete(self, *keys: Any) -> None:
        await self.db.delete(*keys)

    async def expire(self, *, key: str, expire_time_sec: int) -> None:
        try:
            await self.db.expire(key, time=expire_time_sec)
        except Exception as error:
            logger.error(f"Не возможно установить expire: {error}")
            raise ValueError("Не возможно создать запись")


@lru_cache
def get_cache(redis: Redis = Depends(get_redis)) -> Cache:  # type: ignore
    return Cache(db=redis)
