import hashlib
from functools import lru_cache
from random import randbytes
from typing import NoReturn

from fastapi import Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import EmailStr
from redis import Redis
from structlog import get_logger

from src.core.config import settings
from src.db.redis import get_redis
from src.models import User
from src.services.cache import Cache

logger = get_logger()

env = Environment(
    loader=PackageLoader("src", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.cache = Cache(db=self.redis)

    @property
    def config(self) -> ConnectionConfig:
        connect_config = ConnectionConfig(
            MAIL_DEBUG=settings.debug,
            MAIL_USERNAME=settings.email.username,  # pylint: disable=no-member
            MAIL_PASSWORD=settings.email.password,  # pylint: disable=no-member
            MAIL_FROM=settings.email.email,  # pylint: disable=no-member
            MAIL_PORT=settings.email.port,  # pylint: disable=no-member
            MAIL_SERVER=settings.email.host,  # pylint: disable=no-member
            MAIL_FROM_NAME=settings.email.sender,  # pylint: disable=no-member
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

        return connect_config

    async def send_mail(
        self, url: str, subject: str, template: str, emails: list[EmailStr]
    ) -> NoReturn:

        # Generate the HTML template base on the template name
        template = env.get_template(f"{template}.html")

        html = template.render(url=url, subject=subject)

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=emails, body=html, subtype="html"
        )

        # Send the email
        fm = FastMail(self.config)
        logger.info("Send message")
        try:
            await fm.send_message(message)
        except Exception as error:
            logger.error("Send message error", error=f"{error}")

        logger.info("Message sent")

    async def send_verification_code(self, user: User) -> NoReturn:

        token = randbytes(10)
        hashedCode = hashlib.sha256()
        hashedCode.update(token)
        verification_code = hashedCode.hexdigest()

        await self.cache.set(key=f"{verification_code}", value=f"{user.id}")
        await self.cache.expire(
            key=f"{verification_code}",
            expire_time_sec=settings.email.verification_code_expire_sec,  # pylint: disable=no-member
        )

        url = f"{settings.email.verification_code_url}/{token.hex()}"  # pylint: disable=no-member

        await self.send_mail(
            url=url,
            emails=[user.email],
            subject="Для завершения регистрации подтвердите свой email",
            template="verification",
        )


@lru_cache()
def get_email_service(
    redis: Redis = Depends(get_redis),
) -> EmailService:
    return EmailService(redis=redis)
