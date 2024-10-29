import uuid
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from asgi_correlation_id.middleware import is_valid_uuid4
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api import v1
from src.core.config import settings
from src.db import postgresql, redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis.pool = redis.ConnectionPool.from_url(
        settings.redis.cache_dsn,  # type: ignore # pylint: disable=no-member
        decode_responses=True,
    )

    redis.redis = redis.Redis(connection_pool=redis.pool)

    yield

    # Отключаемся от баз при выключении сервера
    await redis.pool.disconnect()


app = FastAPI(
    title=settings.app_name,
    # Адрес документации в красивом интерфейсе
    redoc_url="/redoc",
    docs_url="/docs",
    # Адрес документации в формате OpenAPI
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    version=settings.app_version,
    lifespan=lifespan,
    root_path="/api",
)


app.add_middleware(
    CorrelationIdMiddleware,
    # The HTTP header key to read IDs from.
    header_name="X-Request-ID",
    # Enforce UUID formatting to limit chance of collisions
    # - Invalid header values are discarded, and an ID is generated in its place
    generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    transformer=lambda a: a,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> ORJSONResponse:
    return await http_exception_handler(  # type: ignore
        request,
        HTTPException(
            500,
            "Internal server error",
            headers={
                "X-Request-ID": correlation_id.get() or "",
                "Access-Control-Expose-Headers": "X-Request-ID",
            },
        ),
    )


@app.middleware("http")
async def db_session_middleware(request: Request, call_next: Any) -> Any:
    response = Response(
        "Internal server error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    try:
        postgresql.set_db_session_context(session_id=hash(request))
        response = await call_next(request)
    finally:
        await postgresql.AsyncScopedSession.remove()
        postgresql.set_db_session_context(session_id=None)
    return response


# exception handler for authjwt
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Подключаем роутер к серверу, указав префикс /api/v1/<service>
app.include_router(v1.app_router, prefix="/v1")


if __name__ == "__main__":
    # Приложение должно запускаться с помощью команды
    # `gunicorn main:app --workers $NUM_WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
    # Но таким способом проблематично запускать сервис в дебагере,
    # поэтому сервер приложения для отладки запускаем здесь
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
