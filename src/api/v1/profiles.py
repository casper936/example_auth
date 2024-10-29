import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.route_classes import ThreadLocalDataRouter
from src.schemas import (
    RequestUserProfileCreateSchema,
    UserProfileCreateSchema,
    UserProfileFullSchema,
    UserProfileUpdateSchema,
)
from src.services.crud.profiles import ProfileService, get_profile_service
from src.utils.db import transactional
from src.utils.users import require_user

# Объект router, в котором регистрируем обработчики
router = APIRouter(route_class=ThreadLocalDataRouter)
logger = structlog.get_logger(__name__)


@router.post("/", response_model=UserProfileFullSchema)
@transactional
async def create_profile(
    user_id: str = Depends(require_user),
    service: ProfileService = Depends(get_profile_service),
    *,
    obj_in: RequestUserProfileCreateSchema,
) -> UserProfileFullSchema:
    """Метод создает профиль пользователя"""

    log = logger.bind(user_id=f"{user_id}")

    exists_profile = await service.find_one(filters={"user_id": user_id})

    if exists_profile:
        log.warning("User profile exists", profile_id=f"{exists_profile.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Профиль пользователя уже создан",
        )

    new_obj = UserProfileCreateSchema(user_id=user_id, **obj_in.model_dump())

    try:
        profile = await service.create(obj_in=new_obj)
    except Exception as error:
        log.error("User profile not created", error=f"{error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать профиль пользователя",
        )

    log.info("User profile created")

    return profile


@router.patch("/", response_model=UserProfileFullSchema)
@transactional
async def update_profile(
    user_id: str = Depends(require_user),
    service: ProfileService = Depends(get_profile_service),
    *,
    obj_in: UserProfileUpdateSchema,
) -> UserProfileFullSchema:
    """Метод обновляет профиль пользователя"""

    log = logger.bind(user_id=f"{user_id}")

    db_obj = await service.find_one(filters={"user_id": user_id})

    if not db_obj:
        log.warning("User profile not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пользователя не найден",
        )

    try:
        profile = await service.update(db_obj=db_obj, obj_in=obj_in)
    except Exception as error:
        log.error("User profile update error", error=f"{error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить профиль пользователя",
        )

    return profile
