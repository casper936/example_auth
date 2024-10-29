import structlog
import uuid

from typing import Callable, Coroutine, Any
from fastapi import Request, Response
from fastapi.routing import APIRoute


class ThreadLocalDataRouter(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(
                view=request.url,
                request_id=str(uuid.uuid4()),
                peer=request.client.host        # type: ignore
            )

            return response
        return custom_route_handler
