from typing import Any, Generic, Mapping, Sequence, TypeVar
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import BaseServiceModel

ModelT = TypeVar("ModelT", bound=BaseServiceModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, entity_id: int | None = None, model: type[Any] | None = None, **filters: Any) -> Any | None:
        target_model = model or self.model
        stmt = select(target_model).where(target_model.is_deleted.is_(False))
        if entity_id is not None:
            stmt = stmt.where(target_model.id == entity_id)
        if filters:
            stmt = stmt.filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_paginated_list(self, limit: int, offset: int) -> tuple[Sequence[ModelT], bool]:
        stmt = (
            select(self.model)
            .where(self.model.is_deleted.is_(False))
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit + 1)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        has_next = len(items) > limit
        return items[:limit], has_next

    async def create(self, instance: Any | None = None, model: type[Any] | None = None, **values: Any) -> Any:
        if instance is None:
            target_model = model or self.model
            instance = target_model(**values)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def flush(self) -> None:
        await self.session.flush()

    async def update(self, entity_id: int, values: Mapping[str, Any], model: type[BaseServiceModel] | None = None) -> None:
        target_model = model or self.model
        await self.session.execute(
            update(target_model)
            .filter_by(id=entity_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def delete(self, entity_id: int, model: type[BaseServiceModel] | None = None) -> None:
        target_model = model or self.model
        await self.session.execute(
            update(target_model)
            .filter_by(id=entity_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )
