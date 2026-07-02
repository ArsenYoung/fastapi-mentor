from typing import Mapping

from sqlalchemy import select

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository[PersonsOrm]):
    model = PersonsOrm

    async def update_passport(
        self,
        passport: PassportsOrm,
        values: Mapping[str, object],
    ) -> PassportsOrm:
        for field, value in values.items():
            setattr(passport, field, value)
        return passport

    async def delete_passport(self, passport: PassportsOrm) -> None:
        passport.is_deleted = True

    async def get_person_by_passport_number(
        self,
        passport_number: str,
    ) -> PersonsOrm | None:
        stmt = (
            select(PersonsOrm)
            .join(PassportsOrm)
            .where(
                PersonsOrm.is_deleted.is_(False),
                PassportsOrm.is_deleted.is_(False),
                PassportsOrm.number == passport_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
