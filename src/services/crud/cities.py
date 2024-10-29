from functools import lru_cache

from dadata import DadataAsync
from structlog import get_logger

from src.core.config import settings
from src.db.postgresql import get_current_session
from src.models import City
from src.schemas import UserProfileCreateSchema, UserProfileUpdateSchema
from src.services.crud import CRUDBase

logger = get_logger()


class CityService(CRUDBase[City, UserProfileCreateSchema, UserProfileUpdateSchema]):

    @staticmethod
    async def dadata_search(name: str) -> None:

        async with DadataAsync(
            token=settings.dadata.token,  # pylint: disable=no-member
            secret=settings.dadata.secret,  # pylint: disable=no-member
        ) as dadata:
            return await dadata.suggest(name="address", query=name)


@lru_cache
def get_city_service() -> CityService:
    return CityService(model=City, session_or_factory=get_current_session())
