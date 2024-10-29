import hashlib
from datetime import UTC, datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import EmailStr
from starlette.background import BackgroundTask

from src.core.route_classes import ThreadLocalDataRouter
from src.schemas import (
    RequestUserCreateSchema,
    UserCreateSchema,
    UserFullSchema,
    UserSchema,
    UserVerifySchema,
)
from src.services.cache import Cache, get_cache
from src.services.crud.users import UserService, get_user_service
from src.services.email import EmailService, get_email_service
from src.utils.db import transactional
from src.utils.users import require_user

# Объект router, в котором регистрируем обработчики
router = APIRouter(route_class=ThreadLocalDataRouter)
logger = structlog.get_logger(__name__)


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserSchema
)
@transactional
async def create_user(
    service: UserService = Depends(get_user_service),
    email_service: EmailService = Depends(get_email_service),
    *,
    obj_in: RequestUserCreateSchema,
) -> ORJSONResponse:
    """Ручка отвечающая за предварительную регистраию пользователя"""

    check_exists = await service.find_one(filters={"email": obj_in.email})

    log = logger.bind()

    if check_exists and check_exists.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с указанным email уже существует",
        )
    user = check_exists
    if not user:
        try:
            user = await service.create(
                obj_in=UserCreateSchema(
                    username=obj_in.email,
                    email=obj_in.email,
                    password=obj_in.password,
                )
            )
        except Exception as error:
            log.error("User not created", username=f"{obj_in.email}", error=f"{error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не зарегистрирован",
            )

    user_schema = UserSchema.model_validate(user).model_dump()
    task = BackgroundTask(email_service.send_verification_code, user=user)

    return ORJSONResponse(
        jsonable_encoder(user_schema),
        background=task,
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/verifyemail/{token}", status_code=status.HTTP_202_ACCEPTED)
@transactional
async def verify_email(
    cache: Cache = Depends(get_cache),
    service: UserService = Depends(get_user_service),
    *,
    token: str,
) -> None:
    """Метод валидации email пользователя по полученному в письме токену"""
    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(token))
    verification_code = hashedCode.hexdigest()

    user_id = await cache.get(key=f"{verification_code}")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code or account already verified",
        )

    user = await service.get(item_id=UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid verification code"
        )
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid verification code or account already verified",
        )

    await cache.delete(f"{verification_code}")
    obj_in = UserVerifySchema(
        email_verified=True,
        email_verified_at=datetime.now(UTC),
        is_active=True,
    )

    logger.info("Verify user email")
    await service.update(db_obj=user, obj_in=obj_in)

    return ORJSONResponse(
        {"status": "success", "message": "Аккаунт успешно активирован"}
    )


@router.get("/send/verify/{email}", status_code=status.HTTP_200_OK)
async def send_verify_token(
    request: Request,
    service: UserService = Depends(get_user_service),
    email_service: EmailService = Depends(get_email_service),
    *,
    email: EmailStr,
) -> ORJSONResponse:
    """
    Метод повторно отправляет ссылку на подтверждение email пользователя если учетная запись не подтверждена
    """

    user = await service.find_one(filters={"email": email.lower()})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с указанным email не найден",
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Аккаунт уже активирован"
        )

    task = BackgroundTask(email_service.send_verification_code, user=user)
    return ORJSONResponse(
        {"status": "success", "message": "Письмо отправлено на указанную почту"},
        background=task,
    )


@router.get("/whoami", response_model=UserFullSchema)
async def whoami(
    service: UserService = Depends(get_user_service),
    user_id: str = Depends(require_user),
) -> UserFullSchema:
    """
    Метод получает информацию об авторизованном пользователе
    """
    # We do not need to make any changes to our protected endpoints. They
    # will all still function the exact same as they do when sending the
    # JWT in via a headers instead of a cookies

    return await service.get(item_id=user_id)
