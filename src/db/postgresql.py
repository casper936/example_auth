from contextvars import ContextVar

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    async_scoped_session,
    AsyncSession,
)

from src.core.config import settings

db_session_context: ContextVar[int | None] = ContextVar(
    "db_session_context", default=None
)

engine = create_async_engine(
    str(settings.db.pg_dsn), echo=settings.debug  # pylint: disable=no-member
)


def get_db_session_context() -> int:
    session_id = db_session_context.get()

    if not session_id:
        raise ValueError("Currently no session is available")

    return session_id


def set_db_session_context(*, session_id: int | None) -> None:
    db_session_context.set(session_id)


AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

AsyncScopedSession = async_scoped_session(
    session_factory=AsyncSessionLocal,
    scopefunc=get_db_session_context,
)


# Функция понадобится при внедрении зависимостей
def get_current_session() -> AsyncSession:
    return AsyncScopedSession()
