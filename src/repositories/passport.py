from sqlalchemy import select

from src.models.passports import PassportsOrm
from src.repositories.base import BaseRepository


class PassportRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_id_active(self, passport_id: int) -> PassportsOrm | None:
        return await self.fetch_active_one(
            PassportsOrm,
            id=passport_id,
        )

    async def get_by_id_any(self, passport_id: int) -> PassportsOrm | None:
        return await self.fetch_one(
            select(PassportsOrm)
            .filter_by(id=passport_id)
        )

    async def get_by_person_id_active(self, person_id: int) -> PassportsOrm | None:
        return await self.fetch_active_one(
            PassportsOrm,
            person_id=person_id,
        )

    async def get_by_person_ids(self, person_ids: list[int]) -> list[PassportsOrm]:
        return await self.fetch_active_in(
            PassportsOrm,
            PassportsOrm.person_id,
            person_ids,
            order_by=PassportsOrm.id,
        )

    async def insert(self, person_id: int, number: str, registrated_in: str) -> PassportsOrm:
        return await self.insert_instance(
            PassportsOrm(
                person_id=person_id,
                number=number,
                registrated_in=registrated_in,
            )
        )

    async def update_by_person_id(self, person_id: int, values: dict) -> None:
        await self.update_where(
            PassportsOrm,
            values,
            person_id=person_id,
        )

    async def soft_delete_by_person_id(self, person_id: int) -> None:
        await self.soft_delete_where(
            PassportsOrm,
            person_id=person_id,
        )
