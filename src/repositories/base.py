from pydantic import BaseModel
from sqlalchemy import insert, select


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
        query = select(self.model).filter_by(**filter_by)
        query_result = await self.session.execute(query)
        return query_result.scalars().one_or_none()
    
    async def get_all(self, *filter, **filter_by) -> list[BaseModel] | None:
        query = select(self.model)
        if filter:
            query = query.filter(*filter)
        if filter_by:
            query = query.filter_by(**filter_by)
        
        result = await self.session.execute(query)
        return result.scalars().all()
