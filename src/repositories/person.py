from sqlalchemy import select

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository[PersonsOrm]):
    model = PersonsOrm

    async def get_person_by_passport_number(
        self,
        passport_number: str,
        *,
        for_update: bool = False,
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
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_passport_by_person_id(
        self,
        person_id: int,
        *,
        for_update: bool = False,
    ) -> PassportsOrm | None:
        stmt = select(PassportsOrm).where(
            PassportsOrm.is_deleted.is_(False),
            PassportsOrm.person_id == person_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
