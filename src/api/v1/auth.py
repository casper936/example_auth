from typing import Annotated

import structlog
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import settings
from src.core.route_classes import ThreadLocalDataRouter
from src.schemas import CreateUserSingInSchema
from src.services.crud.users import UserService, get_user_service
from src.utils.db import transactional
from src.utils.users import get_platform, require_user

# Объект router, в котором регистрируем обработчики
router = APIRouter(route_class=ThreadLocalDataRouter)
logger = structlog.get_logger(__name__)
auth_dep = AuthJWTBearer()


@router.post("/login", status_code=status.HTTP_200_OK)
@transactional
async def login(
    request: Request,
    service: UserService = Depends(get_user_service),
    authorize: AuthJWT = Depends(auth_dep),
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> ORJSONResponse:
    """Метод авторизации пользователей"""

    # Check if the user exist
    user = await service.find_one(filters={"username": f"{form_data.username}"})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный логин или пароль",
        )

    # Check if user verified his email
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пожалуйста, подтвержите ваш email",
        )

    # Check if the password is valid
    if not user.verify_password(password=form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный логин или пароль",
        )
    user_agent = request.headers.get("user-agent", "")
    sec_ch_ua_platform = request.headers.get("sec-ch-ua-platform", "")

    user_sign_in = CreateUserSingInSchema(
        user_id=user.id,
        user_agent=user_agent,
        user_platform=sec_ch_ua_platform,
        user_device_type=get_platform(user_agent),
    )

    await service.create_user_sign_in(obj_in=user_sign_in)

    # Create access token
    access_token = await authorize.create_access_token(
        subject=str(user.id),
        expires_time=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
    )

    # Create refresh token
    refresh_token = await authorize.create_refresh_token(
        subject=str(user.id),
        expires_time=settings.auth.REFRESH_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
    )

    response = ORJSONResponse({"access_token": access_token})

    # Set the JWT cookies in the response
    await authorize.set_access_cookies(access_token, response=response)
    await authorize.set_refresh_cookies(refresh_token, response=response)

    response.set_cookie(
        key="logged_in",
        value="True",
        max_age=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
        expires=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
        path="/",
        domain=None,
        secure=False,
        httponly=False,
        samesite="lax",
    )

    return response


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    authorize: AuthJWT = Depends(auth_dep),
    service: UserService = Depends(get_user_service),
):
    """Метод выдает новый access token"""
    try:
        await authorize.jwt_refresh_token_required()

        user_id = await authorize.get_jwt_subject()

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token",
            )

        user = service.get(item_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user belonging to this token no logger exist",
            )
        # Create access token
        access_token = await authorize.create_access_token(
            subject=str(user.id),
            expires_time=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
        )
    except Exception as e:
        error = e.__class__.__name__
        if error == "MissingTokenError":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide refresh token",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response = ORJSONResponse({"access_token": access_token})

    await authorize.set_access_cookies(access_token, response=response)

    response.set_cookie(
        key="logged_in",
        value="True",
        max_age=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
        expires=settings.auth.ACCESS_TOKEN_EXPIRES_IN,  # pylint: disable=no-member
    )

    return response


@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout(
    authorize: AuthJWT = Depends(auth_dep),
    user_id: str = Depends(require_user),
) -> ORJSONResponse:
    """
    Метод разлогинивает пользователя
    """
    # Because the JWT are stored in an httponly cookie now, we cannot
    # log the user out by simply deleting the cookies in the frontend.
    # We need the backend to send us a response to delete the cookies.

    await authorize.jwt_required()

    await authorize.unset_jwt_cookies()

    response = ORJSONResponse({"status": "success"})
    response.set_cookie("logged_in", "", -1)

    return response
