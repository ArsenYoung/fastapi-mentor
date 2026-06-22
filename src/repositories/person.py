from typing import Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository):
    model = PersonsOrm

    def _get_with_passport_stmt(self):
        return (
            select(PersonsOrm)
            .where(PersonsOrm.is_deleted.is_(False))
            .options(
                joinedload(
                    PersonsOrm.passport.and_(PassportsOrm.is_deleted.is_(False))
                )
            )
            .order_by(PersonsOrm.id)
        )

    async def _get_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        stmt = self._get_with_passport_stmt().where(PersonsOrm.id == person_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_person_by_passport_number(self, number: str) -> PersonsOrm | None:
        stmt = (
            select(PersonsOrm)
            .join(PersonsOrm.passport)
            .where(
                PassportsOrm.number == number,
            )
            .options(
                joinedload(PersonsOrm.passport)
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        return await self._get_person_with_passport(person_id)

    async def create_person_with_passport(self, person: PersonsOrm) -> PersonsOrm:
        self.session.add(person)
        await self.session.flush()
        created_person = await self._get_person_with_passport(person.id)
        assert created_person is not None
        return created_person

    async def get_persons_with_passports_paginated_list(
        self,
        limit: int,
        offset: int,
    ) -> Tuple[Sequence[PersonsOrm], bool]:
        stmt = self._get_with_passport_stmt().offset(offset).limit(limit + 1)
        result = await self.session.execute(stmt)
        persons = list(result.unique().scalars().all())
        has_next = len(persons) > limit
        return persons[:limit], has_next
