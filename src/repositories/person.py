from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository):
    model = PersonsOrm

    def __init__(self, session):
        self.session = session

    async def insert(self, first_name: str, last_name: str) -> PersonsOrm:
        return await self.insert_model(
            first_name=first_name,
            last_name=last_name,
        )
