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

    async def count_active(self, model: type[ModelT], **filters: Any) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(model)
            .filter_by(**filters, is_deleted=False)
        )
        return result.scalar_one()

    async def get_one(self, stmt) -> ModelT | None:
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_one_active(self, model: type[ModelT], **filters: Any) -> ModelT | None:
        stmt = select(model).filter_by(**filters, is_deleted=False)
        return await self.get_one(stmt)
    
    async def get_many(self, stmt) -> list[ModelT]:
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_many_active(self, model: type[ModelT], **filters: Any) -> list[ModelT]:
        stmt = select(model).filter_by(**filters, is_deleted=False)
        return await self.get_many(stmt)

    async def get_page_active(
        self, 
        model: type[ModelT], 
        limit:int, 
        offset: int, 
        order_by: Any | None = None,
        **filters: Any,
    ) -> tuple[list[ModelT], int]:
        stmt = select(model).filter_by(**filters, is_deleted=False)
        if order_by:
            stmt = stmt.order_by(order_by)
        items_result = await self.session.execute(stmt.offset(offset).limit(limit))
        items = list(items_result.scalars().all())
        total = await self.count_active(model, **filters)
        return items, total
    
    async def get_many_active_in(
        self,
        model: type[ModelT],
        column: Any,
        values: Iterable[Any],
        order_by: Any | None = None
    ) -> list[ModelT]:
        values = list(values)
        if not values:
            return []
        stmt = select(model).where(
            column.in_(values),
            model.is_deleted.is_(False)
        )
        if order_by:
            stmt = stmt.order_by(order_by)
        return await self.get_many(stmt)

    async def get_latest_one(self, model: type[ModelT], order_by: Any, **filters: Any) -> ModelT | None:
        stmt = (
            select(model)
            .filter_by(**filters)
            .order_by(order_by.desc())
        )
        return await self.get_one(stmt)
    
    async def insert_instance(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def insert_model(self, **values: Any) -> ModelT:
        return await self.insert_instance(self._get_model()(**values))
    
    async def update_where(self, model: type[ModelT], values: dict[str, Any], **filters: Any) -> int:
        result = await self.session.execute(
            update(model)
            .filter_by(**filters)
            .values(values)
        )
        return result.rowcount or 0
    
    async def soft_delete_where(self, model: type[ModelT], **filters: Any) -> int:
        return await self.update_where(
            model, 
            {"is_deleted": True},
            **filters
        )

    async def get_by_id_active(self, entity_id: int) -> ModelT | None:
        return await self.get_one_active(
            self._get_model(),
            id=entity_id,
        )

    async def get_by_id_any(self, entity_id: int) -> ModelT | None:
        return await self.get_one(
            select(self._get_model())
            .filter_by(id=entity_id)
        )

    async def get_page(self, limit: int, offset: int, **filters: Any) -> tuple[list[ModelT], int]:
        model = self._get_model()
        return await self.get_page_active(
            model,
            limit=limit,
            offset=offset,
            order_by=model.id,
            **filters,
        )

    async def update(self, entity_id: int, values: dict[str, Any]) -> None:
        await self.update_where(
            self._get_model(),
            values,
            id=entity_id,
        )

    async def soft_delete(self, entity_id: int) -> None:
        await self.soft_delete_where(
            self._get_model(),
            id=entity_id,
        )

    async def restore(self, entity_id: int) -> None:
        await self.update_where(
            self._get_model(),
            {"is_deleted": False},
            id=entity_id,
        )
        

    
