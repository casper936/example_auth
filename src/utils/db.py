import functools
from typing import Any, Awaitable, Callable

import structlog

from src.db.postgresql import get_current_session, get_db_session_context

AsyncCallable = Callable[..., Awaitable]
logger = structlog.get_logger()


def transactional(func: AsyncCallable) -> AsyncCallable:
    @functools.wraps(func)
    async def _wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
        try:
            db_session = get_current_session()

            if db_session.in_transaction():
                return await func(*args, **kwargs)

            async with db_session.begin():
                # automatically committed / rolled back thanks to the context manager
                return_value = await func(*args, **kwargs)

            return return_value
        except Exception as error:
            logger.info(f"request hash: {get_db_session_context()}")
            logger.error(f"{error}")
            raise

    return _wrapper
