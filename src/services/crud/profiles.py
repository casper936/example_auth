from functools import lru_cache

from structlog import get_logger

from src.db.postgresql import get_current_session
from src.models import Profile
from src.schemas import UserProfileCreateSchema, UserProfileUpdateSchema
from src.services.crud import CRUDBase

logger = get_logger()


class ProfileService(
    CRUDBase[Profile, UserProfileCreateSchema, UserProfileUpdateSchema]
):
    pass


@lru_cache
def get_profile_service() -> ProfileService:
    return ProfileService(model=Profile, session_or_factory=get_current_session())
