from redis.asyncio import ConnectionPool, Redis

redis: Redis = None  # type: ignore
pool: ConnectionPool = None  # type: ignore


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis
