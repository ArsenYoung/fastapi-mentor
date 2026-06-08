from collections.abc import Iterable

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonsPassportsRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_person(self, person_id: int) -> PersonsOrm | None:
        return await self.fetch_active_one(PersonsOrm, id=person_id)

    async def get_passport(self, person_id: int) -> PassportsOrm | None:
        return await self.fetch_active_one(PassportsOrm, person_id=person_id)

    async def get_persons_page(self, limit: int, offset: int) -> tuple[list[PersonsOrm], int]:
        return await self.fetch_active_page(
            PersonsOrm,
            limit=limit,
            offset=offset,
            order_by=PersonsOrm.id,
        )

    async def get_passports_by_person_ids(self, person_ids: Iterable[int]) -> list[PassportsOrm]:
        return await self.fetch_active_in(
            PassportsOrm,
            PassportsOrm.person_id,
            person_ids,
            order_by=PassportsOrm.id,
        )

    async def insert_person(self, first_name: str, last_name: str) -> PersonsOrm:
        return await self.insert_instance(
            PersonsOrm(
                first_name=first_name,
                last_name=last_name,
            )
        )

    async def insert_passport(self, person_id: int, number: str, registrated_in: str) -> PassportsOrm:
        return await self.insert_instance(
            PassportsOrm(
                person_id=person_id,
                number=number,
                registrated_in=registrated_in,
            )
        )

    async def update_person(self, person_id: int, values: dict) -> None:
        await self.update_where(
            PersonsOrm,
            values,
            id=person_id,
        )

    async def update_passport(self, person_id: int, values: dict) -> None:
        await self.update_where(
            PassportsOrm,
            values,
            person_id=person_id,
        )

    async def soft_delete_person(self, person_id: int) -> None:
        await self.soft_delete_where(
            PersonsOrm,
            id=person_id,
        )

    async def soft_delete_passport(self, person_id: int) -> None:
        await self.soft_delete_where(
            PassportsOrm,
            person_id=person_id,
        )
