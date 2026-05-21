from pydantic import BaseModel
from sqlalchemy import insert


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def add(self, data: BaseModel) -> BaseModel:
        query = insert(self.model).values(**data.model_dump()).returning(self.model)
        return await self.session.execute(query)