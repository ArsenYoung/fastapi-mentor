from typing import Any, Generic, Iterable, TypeVar
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import BaseServiceModel

ModelT = TypeVar("ModelT", bound=BaseServiceModel)

class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_model(self) -> type[ModelT]:
        return self.model

    def _build_select(
        self,
        model: type[ModelT],
        *,
        active_only: bool,
        order_by: Any | None = None,
        descending: bool = False,
        in_filter: tuple[Any, Iterable[Any]] | None = None,
        **filters: Any,
    ):
        stmt = select(model)
        if in_filter is not None:
            column, values = in_filter
            stmt = stmt.where(column.in_(values))
        if active_only:
            stmt = stmt.where(model.is_deleted.is_(False))
        if filters:
            stmt = stmt.filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by.desc() if descending else order_by)
        return stmt

    async def _get_one_by_stmt(self, stmt) -> ModelT | None:
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_many_by_stmt(self, stmt) -> list[ModelT]:
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_one(self, model: type[ModelT], **filters: Any) -> ModelT | None:
        stmt = self._build_select(
            model,
            active_only=True,
            **filters,
        )
        return await self._get_one_by_stmt(stmt)

    async def get_many(self, model: type[ModelT], **filters: Any) -> list[ModelT]:
        stmt = self._build_select(
            model,
            active_only=True,
            **filters,
        )
        return await self._get_many_by_stmt(stmt)

    async def get_paginated_list_by_model(
        self, 
        model: type[ModelT], 
        limit:int, 
        offset: int, 
        order_by: Any | None = None,
        **filters: Any,
    ) -> tuple[list[ModelT], bool]:
        stmt = self._build_select(
            model,
            active_only=True,
            order_by=order_by,
            **filters,
        )
        items_result = await self.session.execute(stmt.offset(offset).limit(limit + 1))
        items = list(items_result.scalars().all())
        has_next = len(items) > limit
        return items[:limit], has_next

    async def get_many_in(
        self,
        model: type[ModelT],
        column: Any,
        values: Iterable[Any],
        order_by: Any | None = None
    ) -> list[ModelT]:
        values = list(values)
        if not values:
            return []
        stmt = self._build_select(
            model,
            active_only=True,
            order_by=order_by,
            in_filter=(column, values),
        )
        return await self._get_many_by_stmt(stmt)
    
    async def create(self, **values: Any) -> ModelT:
        instance = self._get_model()(**values)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        return await self.get_one(
            self._get_model(),
            id=entity_id,
        )

    async def get_paginated_list(self, limit: int, offset: int, **filters: Any) -> tuple[list[ModelT], bool]:
        model = self._get_model()
        return await self.get_paginated_list_by_model(
            model,
            limit=limit,
            offset=offset,
            order_by=model.id,
            **filters,
        )

    async def update(self, entity_id: int, values: dict[str, Any]) -> None:
        await self.session.execute(
            update(self._get_model())
            .filter_by(id=entity_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def delete(self, entity_id: int) -> None:
        await self.session.execute(
            update(self._get_model())
            .filter_by(id=entity_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )

    async def acquire_advisory_lock(self, lock_key: str) -> None:
        await self.session.execute(
            select(func.pg_advisory_xact_lock(func.hashtext(lock_key)))
        )
