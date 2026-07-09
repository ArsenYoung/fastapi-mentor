from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.mappers.persons_passports import PersonsPassportsMapper
from src.repositories.person import PersonRepository
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.schemas.errors import PassportErrorDetails, PersonErrorDetails
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    def __init__(self, repo: PersonRepository, mapper: PersonsPassportsMapper):
        self.repo = repo
        self.mapper = mapper

    async def create(self, data: PersonCreate) -> Person:
        existing_person = await self.repo.get_person_by_passport_number(
            data.passport.number
        )
        if existing_person is not None:
            raise AlreadyExistsException(
                message="A person with this passport number already exists",
                details=PassportErrorDetails(
                    passport_number=data.passport.number,
                ),
            )

        person = await self.repo.create(
            self.mapper.map_person_create_to_orm(data),
        )
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=person.passport.id,
        )
        return self.mapper.map_person_to_read(person)

    async def get(self, person_id: int) -> Person:
        person = await self.repo.get(id=person_id)
        if person is None:
            raise ObjectNotFoundException(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
            )
        return self.mapper.map_person_to_read(person)

    async def get_paginated_list(self, limit: int, offset: int) -> PersonsPaginatedList:
        persons, has_next = await self.repo.get_paginated_list(limit, offset)
        return self.mapper.map_persons_paginated_list(
            persons,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete(self, person_id: int) -> None:
        person = await self.repo.get(id=person_id, for_update=True)
        if person is None:
            raise ObjectNotFoundException(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
            )
        passport = await self.repo.get_passport_by_person_id(
            person_id,
            for_update=True,
        )
        if passport is not None:
            passport.is_deleted = True
        await self.repo.delete(person)
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update(self, person_id: int, data: PersonUpdate) -> None:
        person = await self.repo.get(id=person_id, for_update=True)
        if person is None:
            raise ObjectNotFoundException(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
            )

        passport = data.passport
        passport_number = passport.number if passport is not None else None

        if passport_number is not None:
            existing_person = await self.repo.get_person_by_passport_number(
                passport_number,
            )
            if existing_person is not None and existing_person.id != person_id:
                raise AlreadyExistsException(
                    message="A person with this passport number already exists",
                    details=PassportErrorDetails(
                        passport_number=passport_number,
                    ),
                )

        person_updates = self.mapper.map_person_update_to_fields(data)
        for field_name, value in person_updates.items():
            setattr(person, field_name, value)

        if passport is not None:
            person_passport = await self.repo.get_passport_by_person_id(
                person_id,
                for_update=True,
            )
            passport_updates = self.mapper.map_passport_update_to_fields(passport)
            for field_name, value in passport_updates.items():
                setattr(person_passport, field_name, value)

        await self.repo.update(person)
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
