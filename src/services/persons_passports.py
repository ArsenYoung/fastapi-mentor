from src.exceptions.persons_passports import (
    PassportAlreadyExistsException,
    PersonNotFoundException,
)
from src.mappers.persons_passports import (
    map_person_create_to_orm,
    map_person_to_read,
    map_persons_paginated_list,
)
from src.repositories.person import PersonRepository
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    def __init__(self, repo: PersonRepository):
        self.repo = repo

    async def create(self, data: PersonCreate) -> Person:
        existing_person = await self.repo.get_person_by_passport_number(
            data.passport.number
        )
        if existing_person is not None:
            raise PassportAlreadyExistsException(
                passport_number=data.passport.number,
            )

        person = await self.repo.create(
            map_person_create_to_orm(data),
        )
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=person.passport.id,
        )
        return map_person_to_read(person)

    async def get(self, person_id: int) -> Person:
        person = await self.repo.get(id=person_id)
        if person is None:
            raise PersonNotFoundException(person_id=person_id)
        return map_person_to_read(person)

    async def get_paginated_list(self, limit: int, offset: int) -> PersonsPaginatedList:
        persons, has_next = await self.repo.get_paginated_list(limit, offset)
        return map_persons_paginated_list(
            persons,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete(self, person_id: int) -> None:
        person = await self.repo.get(id=person_id)
        if person is None:
            raise PersonNotFoundException(person_id=person_id)
        person.passport.is_deleted = True
        await self.repo.delete(person)
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update(self, person_id: int, data: PersonUpdate) -> None:
        person = await self.repo.get(id=person_id)
        if person is None:
            raise PersonNotFoundException(person_id=person_id)

        passport = data.passport
        passport_number = passport.number if passport is not None else None

        if passport_number is not None:
            existing_person = await self.repo.get_person_by_passport_number(
                passport_number
            )
            if existing_person is not None and existing_person.id != person_id:
                raise PassportAlreadyExistsException(
                    passport_number=passport_number,
                )

        await self.repo.update(
            person,
            data.model_dump(exclude_unset=True, exclude={"passport"}),
            exclude_none=True,
        )
        if passport is not None:
            await self.repo.update(
                person.passport,
                passport.model_dump(exclude_unset=True),
                exclude_none=True,
            )

        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
