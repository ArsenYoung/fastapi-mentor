from typing import Any, Generic, Sequence, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import BaseServiceModel

ModelT = TypeVar("ModelT", bound=BaseServiceModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        *,
        for_update: bool = False,
        **filters: Any,
    ) -> ModelT | None:
        stmt = (
            select(self.model)
            .where(self.model.is_deleted.is_(False))
            .filter_by(**filters)
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_paginated_list(
        self, limit: int, offset: int
    ) -> tuple[Sequence[ModelT], bool]:
        stmt = (
            select(self.model)
            .where(self.model.is_deleted.is_(False))
            .order_by(self.model.id)
            .offset(offset)
            .limit(limit + 1)
        )
        result = await self.session.execute(stmt)
        items = list(result.unique().scalars().all())
        has_next = len(items) > limit
        return items[:limit], has_next

    async def create(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: ModelT) -> ModelT:
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        instance.is_deleted = True
