from pydantic import BaseModel
from sqlalchemy import insert


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def add(self, data: BaseModel, exclude = {}) -> BaseModel:
        query = insert(self.model).values(**data.model_dump(exclude=exclude)).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().one()
    
    async def add_bulk(self, data: list[BaseModel]):
        query = insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
