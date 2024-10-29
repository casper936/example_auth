from typing import Any, Callable, Generic, Sequence, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base_mixins import BaseMixin

ModelType = TypeVar("ModelType", bound=BaseMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        session_or_factory: AsyncSession | Callable[[], AsyncSession],
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self._session_or_factory = session_or_factory

    @property
    def session(self) -> AsyncSession:
        if isinstance(self._session_or_factory, AsyncSession):
            return self._session_or_factory
        return self._session_or_factory()

    async def filter(self, filters: dict[str, str | list[Any]]) -> list[ModelType]:
        query = select(self.model)
        for field, value in filters.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, field).in_(value))
            else:
                query = query.filter(getattr(self.model, field) == value)
        result = await self.session.execute(query)

        return result.scalars().all()

    async def find_one(self, filters: dict[str, str | list[Any]]) -> ModelType:
        query = select(self.model)
        for field, value in filters.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, field).in_(value))
            else:
                query = query.filter(getattr(self.model, field) == value)
        result = await self.session.execute(query)

        return result.scalars().first()

    async def get(self, item_id: UUID) -> ModelType | None:
        return await self.session.get(entity=self.model, ident=item_id)

    async def list(self, *, skip: int = 1, limit: int = 100) -> Sequence[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip * limit).limit(limit)
        )
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType, **kwargs: Any) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj.__dict__)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data.get(field))

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def remove(self, *, item_id: UUID) -> ModelType:
        remove_db_obj = await self.session.get(entity=self.model, ident=item_id)
        if not remove_db_obj:
            raise ValueError(
                f"DB object ID {item_id} in model {self.model.__name__} not found"
            )

        await self.session.delete(remove_db_obj)
        await self.session.flush()
        return remove_db_obj
