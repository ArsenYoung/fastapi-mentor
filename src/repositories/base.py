from typing import Any, Dict, Generic, TypeVar
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import BaseServiceModel

ModelT = TypeVar("ModelT", bound=BaseServiceModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        stmt = select(self.model).where(
            self.model.id == entity_id,
            self.model.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **values: Any) -> ModelT:
        instance = self.model(**values)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def flush(self) -> None:
        await self.session.flush()

    async def update(self, entity_id: int, values: Dict[str, Any]) -> None:
        await self.session.execute(
            update(self.model)
            .filter_by(id=entity_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def delete(self, entity_id: int) -> None:
        await self.session.execute(
            update(self.model)
            .filter_by(id=entity_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )
