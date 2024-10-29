from functools import lru_cache

from dadata import DadataAsync
from structlog import get_logger

from src.core.config import settings
from src.db.postgresql import get_current_session
from src.models import Company
from src.schemas import UserProfileCreateSchema, UserProfileUpdateSchema
from src.services.crud import CRUDBase

logger = get_logger()


class CompanyService(
    CRUDBase[Company, UserProfileCreateSchema, UserProfileUpdateSchema]
):
    @staticmethod
    async def dadata_search_by_inn(inn: str) -> None:

        async with DadataAsync(
            token=settings.dadata.token,  # pylint: disable=no-member
            secret=settings.dadata.secret,  # pylint: disable=no-member
        ) as dadata:
            return await dadata.find_by_id(name="party", query=inn)


@lru_cache
def get_company_service() -> CompanyService:
    return CompanyService(model=Company, session_or_factory=get_current_session())
