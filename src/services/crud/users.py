from functools import lru_cache
from typing import Any

from structlog import get_logger

from src.db.postgresql import get_current_session
from src.models import User, UserSingIn
from src.schemas import CreateUserSingInSchema, UserCreateSchema, UserUpdateSchema
from src.services.crud import CRUDBase

logger = get_logger()


class UserService(CRUDBase[User, UserCreateSchema, UserUpdateSchema]):
    async def create(self, *, obj_in: UserCreateSchema, **kwargs: Any) -> User:
        user_obj = self.model(**obj_in.model_dump(exclude={"password"}))
        user_obj.set_password(obj_in.password)

        self.session.add(user_obj)
        await self.session.flush()
        await self.session.refresh(user_obj)
        return user_obj

    async def create_user_sign_in(
        self, *, obj_in: CreateUserSingInSchema, **kwargs: Any
    ) -> None:
        db_obj = UserSingIn(**obj_in.model_dump())

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)


@lru_cache
def get_user_service() -> UserService:
    return UserService(model=User, session_or_factory=get_current_session())
