from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Depends, HTTPException, status

from src.core.exceptions import NotVerified, UserNotFound
from src.db.postgresql import get_current_session
from src.models.user import User

auth_dep = AuthJWTBearer()


def get_platform(user_agent: str) -> str:
    """Ищет в UserAgent"""

    phones = (
        "iphone",
        "android",
        "blackberry",
    )

    if any(phone in user_agent.lower() for phone in phones):
        return "mobile"
    else:
        return "web"


async def require_user(authorize: AuthJWT = Depends(auth_dep)):
    db_session = get_current_session()
    try:
        await authorize.jwt_required()
        user_id = await authorize.get_jwt_subject()
        user = await db_session.get(entity=User, ident=user_id)

        if not user:
            raise UserNotFound("User no longer exist")

        if not user.email_verified:
            raise NotVerified("You are not verified")

        if user.is_blocked:
            raise UserNotFound("User no longer exist")

    except Exception as e:
        error = e.__class__.__name__
        if error == "MissingTokenError":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not logged in",
            )
        if error == "UserNotFound":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exist",
            )
        if error == "NotVerified":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your account",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired",
        )
    return user_id
