from sqlalchemy import select

from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_id_active(self, person_id: int) -> PersonsOrm | None:
        return await self.fetch_active_one(
            PersonsOrm,
            id=person_id,
        )

    async def get_by_id_any(self, person_id: int) -> PersonsOrm | None:
        return await self.fetch_one(
            select(PersonsOrm)
            .filter_by(id=person_id)
        )

    async def get_page(self, limit: int, offset: int) -> tuple[list[PersonsOrm], int]:
        return await self.fetch_active_page(
            PersonsOrm,
            limit=limit,
            offset=offset,
            order_by=PersonsOrm.id,
        )

    async def insert(self, first_name: str, last_name: str) -> PersonsOrm:
        return await self.insert_instance(
            PersonsOrm(
                first_name=first_name,
                last_name=last_name,
            )
        )

    async def update(self, person_id: int, values: dict) -> None:
        await self.update_where(
            PersonsOrm,
            values,
            id=person_id,
        )

    async def soft_delete(self, person_id: int) -> None:
        await self.soft_delete_where(
            PersonsOrm,
            id=person_id,
        )
