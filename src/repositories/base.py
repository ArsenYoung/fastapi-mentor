from typing import Any, Generic, Iterable, TypeVar
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import BaseServiceModel

ModelT = TypeVar("ModelT", bound=BaseServiceModel)

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_active(self, model: type[ModelT], **filters: Any) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(model)
            .filter_by(**filters, is_deleted=False)
        )
        return result.scalar_one()

    async def fetch_one(self, stmt) -> ModelT | None:
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def fetch_active_one(self, model: type[ModelT], **filters: Any) -> ModelT | None:
        stmt = select(model).filter_by(**filters, is_deleted=False)
        return await self.fetch_one(stmt)
    
    async def fetch_all(self, stmt) -> list[ModelT]:
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def fetch_active_all(self, model: type[ModelT], **filters: Any) -> list[ModelT]:
        stmt = select(model).filter_by(**filters, is_deleted=False)
        return await self.fetch_all(stmt)

    async def fetch_active_page(
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
    
    async def fetch_active_in(
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
        return await self.fetch_all(stmt)
    
    async def insert_instance(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def insert_returning(self, model: type[ModelT], values: dict[str, Any]) -> ModelT:
        result = await self.session.execute(
            insert(model)
            .values(**values)
            .returning(model)
        )
        return result.scalar_one()
    
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
        

    