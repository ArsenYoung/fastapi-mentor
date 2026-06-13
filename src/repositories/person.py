from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository
from src.schemas.persons import PersonCreate, PersonUpdate


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

    async def _get_person_with_passport_or_none(self, person_id: int) -> PersonsOrm | None:
        stmt = self._get_with_passport_stmt().where(PersonsOrm.id == person_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_person_with_passport(self, data: PersonCreate) -> PersonsOrm | None:
        person = await self.insert(
            first_name=data.first_name,
            last_name=data.last_name,
        )
        self.session.add(
            PassportsOrm(
                person_id=person.id,
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            )
        )
        await self.session.flush()
        return await self._get_person_with_passport_or_none(person.id)

    async def get_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        return await self._get_person_with_passport_or_none(person_id)

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

    async def soft_delete_passport_by_person_id(self, person_id: int) -> None:
        await self.session.execute(
            update(PassportsOrm)
            .filter_by(person_id=person_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )

    async def update_person_with_passport(self, person_id: int, data: PersonUpdate) -> PersonsOrm | None:
        person = await self._get_person_with_passport_or_none(person_id)
        if person is None:
            return None

        person_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"passport"},
        )
        if person_data:
            await self.update(person_id, person_data)

        if data.passport is not None:
            await self.update_passport_by_person_id(
                person_id,
                data.passport.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                ),
            )

        return await self._get_person_with_passport_or_none(person_id)

    async def delete_person_with_passport(self, person_id: int) -> PersonsOrm | None:
        person = await self._get_person_with_passport_or_none(person_id)
        if person is None:
            return None
        await self.soft_delete_passport_by_person_id(person_id)
        await self.soft_delete(person_id)
        return person
