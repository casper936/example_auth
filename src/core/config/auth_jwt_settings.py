import structlog
from async_fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings

from src.db.redis import get_redis
from src.services.cache import Cache

logger = structlog.get_logger(__name__)


class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}

    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies", "headers"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = False
    # TODO: Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    # authjwt_cookie_samesite: str = "lax"


# callback to get async_fastapi_jwt_auth configuration
@AuthJWT.load_config
def get_cfg():
    return AuthJWTSettings()


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    redis = await get_redis()
    cache = Cache(db=redis)

    jti = decrypted_token["jti"]
    try:
        entry = await cache.get(key=f"{jti}")
    except Exception as e:
        logger.error("Get jti error", error=f"{e}")
        raise
    return entry and entry == "true"
