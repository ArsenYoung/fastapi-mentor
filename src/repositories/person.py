from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository[PersonsOrm]):
    model = PersonsOrm

    async def get_person_by_passport_number(self, number: str) -> PersonsOrm | None:
        stmt = (
            select(PersonsOrm)
            .join(PersonsOrm.passport)
            .where(
                PassportsOrm.number == number,
            )
            .options(joinedload(PersonsOrm.passport))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
