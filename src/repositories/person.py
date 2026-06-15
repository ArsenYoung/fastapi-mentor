from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository):
    model = PersonsOrm

    def __init__(self, session):
        self.session = session

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

    async def get_passport_by_number(self, number: str) -> PassportsOrm | None:
        return await self.get_one(
            PassportsOrm,
            number=number,
        )

    async def create_person_with_passport(
        self,
        first_name: str,
        last_name: str,
        passport_number: str,
        registrated_in: str,
    ) -> PersonsOrm:
        person = await self.create(
            first_name=first_name,
            last_name=last_name,
        )
        self.session.add(
            PassportsOrm(
                person_id=person.id,
                number=passport_number,
                registrated_in=registrated_in,
            )
        )
        await self.session.flush()
        created_person = await self._get_person_with_passport(person.id)
        assert created_person is not None
        return created_person

    async def get_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        return await self._get_person_with_passport(person_id)

    async def get_persons_with_passports_paginated_list(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[PersonsOrm], bool]:
        stmt = self._get_with_passport_stmt().offset(offset).limit(limit + 1)
        result = await self.session.execute(stmt)
        persons = list(result.unique().scalars().all())
        has_next = len(persons) > limit
        return persons[:limit], has_next

    async def update_passport_by_person_id(self, person_id: int, values: dict) -> None:
        await self.session.execute(
            update(PassportsOrm)
            .filter_by(person_id=person_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def delete_passport_by_person_id(self, person_id: int) -> None:
        await self.session.execute(
            update(PassportsOrm)
            .filter_by(person_id=person_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )

    async def update_person_with_passport(
        self,
        person_id: int,
        person_values: dict,
        passport_values: dict,
    ) -> PersonsOrm | None:
        person = await self._get_person_with_passport(person_id)
        if person is None:
            return None

        if person_values:
            await self.update(person_id, person_values)

        if passport_values:
            await self.update_passport_by_person_id(person_id, passport_values)

        return await self._get_person_with_passport(person_id)

    async def delete_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        person = await self._get_person_with_passport(person_id)
        if person is None:
            return None
        await self.delete_passport_by_person_id(person_id)
        await self.delete(person_id)
        return person
