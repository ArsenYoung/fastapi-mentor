from src.mappers.persons_passports import (
    map_passport_create_to_orm,
    map_person_to_read,
    map_persons_paginated_list,
)
from src.models.persons import PersonsOrm
from src.repositories.person import PersonRepository
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    def __init__(self, repo: PersonRepository):
        self.repo = repo

    async def _get_existing_person(self, person_id: int) -> PersonsOrm:
        person = await self.repo.get_person_with_passport(person_id)
        if person is None:
            self._raise_not_found(
                message="Person not found",
                details={"person_id": person_id},
                person_id=person_id,
            )
        return person

    async def _raise_if_passport_number_exists(
        self,
        passport_number: str,
        *,
        exclude_person_id: int | None = None,
    ) -> None:
        person = await self.repo.get_person_by_passport_number(passport_number)
        if person is None or person.id == exclude_person_id:
            return
        self._raise_already_exists(
            message="A person with this passport number already exists",
            details={"passport_number": passport_number},
            passport_number=passport_number,
        )

    async def create_person_with_passport(self, data: PersonCreate) -> None:
        await self._raise_if_passport_number_exists(data.passport.number)
        person_data = data.model_dump(exclude={"passport"})
        person = await self.repo.create(**person_data)
        passport = map_passport_create_to_orm(data.passport, person.id)
        self.repo.session.add(passport)
        await self.repo.flush()
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=passport.id,
        )

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self._get_existing_person(person_id)
        return map_person_to_read(person)

    async def get_persons_with_passports_paginated_list(self, limit: int, offset: int) -> PersonsPaginatedList:
        persons, has_next = await self.repo.get_persons_with_passports_paginated_list(limit, offset)
        return map_persons_paginated_list(
            persons,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete_person_with_passport(self, person_id: int) -> None:
        person = await self._get_existing_person(person_id)
        person.passport.is_deleted = True
        await self.repo.delete(person.id)
        await self.repo.flush()
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update_person_with_passport(self, person_id: int, data: PersonUpdate) -> None:
        person = await self._get_existing_person(person_id)

        person_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"passport"},
        )
        for field, value in person_data.items():
            setattr(person, field, value)
        if data.passport is not None:
            if data.passport.number is not None:
                await self._raise_if_passport_number_exists(
                    data.passport.number,
                    exclude_person_id=person_id,
                )
            passport_data = data.passport.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )
            for field, value in passport_data.items():
                setattr(person.passport, field, value)
        await self.repo.flush()
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
