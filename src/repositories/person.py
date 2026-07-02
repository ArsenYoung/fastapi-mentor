from typing import Any, Sequence

from sqlalchemy import select

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository


class PersonRepository(BaseRepository[PersonsOrm]):
    model = PersonsOrm

    async def get(self, **filters: Any) -> PersonsOrm | None:
        stmt = (
            select(PersonsOrm)
            .join(PassportsOrm)
            .where(
                PersonsOrm.is_deleted.is_(False),
                PassportsOrm.is_deleted.is_(False),
            )
        )
        for field, value in filters.items():
            stmt = stmt.where(getattr(PersonsOrm, field) == value)

        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_paginated_list(
        self,
        limit: int,
        offset: int,
    ) -> tuple[Sequence[PersonsOrm], bool]:
        stmt = (
            select(PersonsOrm)
            .join(PassportsOrm)
            .where(
                PersonsOrm.is_deleted.is_(False),
                PassportsOrm.is_deleted.is_(False),
            )
            .order_by(PersonsOrm.id)
            .offset(offset)
            .limit(limit + 1)
        )
        result = await self.session.execute(stmt)
        items = list(result.unique().scalars().all())
        has_next = len(items) > limit
        return items[:limit], has_next

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
