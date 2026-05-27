from pydantic import BaseModel
from sqlalchemy import insert, select, update


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def add(self, data: BaseModel, exclude = {}) -> BaseModel:
        query = insert(self.model).values(**data.model_dump(exclude=exclude)).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().one()
    
    async def add_bulk(self, data: list[BaseModel]) -> list[BaseModel]:
        query = insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by, is_deleted=False)
        query_result = await self.session.execute(query)
        return query_result.scalars().one_or_none()
    
    async def get_all(self, *filter, **filter_by) -> list[BaseModel] | None:
        query = select(self.model)
        if filter:
            query = query.filter(*filter, is_deleted=False)
        if filter_by:
            query = query.filter_by(**filter_by, is_deleted=False)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def delete(self, **filter_by) -> None:
        query = (
            update(self.model)
            .filter_by(**filter_by)
            .values(is_deleted=True)
        )
        await self.session.execute(query)

    async def delete_bulk_by_ids(self, ids: list[int]) -> list[BaseModel]:
        query = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(is_deleted=True)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(
        self,
        data: dict,
        **filter_by,
    ) -> None:
        query = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data)
        )
        await self.session.execute(query)
