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
        person = await self.repo.create(
            self.mapper.map_person_create_to_orm_without_passport(data),
        )
        passport = await self.repo.create_passport_do_nothing(
            self.mapper.map_passport_create_to_insert_values(
                person_id=person.id,
                data=data.passport,
            ),
        )
        if passport is None:
            raise AlreadyExistsException(
                message="A person with this passport number already exists",
                details=PassportErrorDetails(
                    passport_number=data.passport.number,
                ),
            )

        person.passport = passport
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

        self.mapper.apply_person_update_to_orm(data, person)

        if passport is not None:
            has_passport_updates = (
                passport.number is not None
                or passport.registrated_in is not None
            )
            if has_passport_updates:
                person_passport = await self.repo.get_passport_by_person_id(
                    person_id,
                    for_update=True,
                )
                passport_number = passport.number
                if (
                    passport_number is not None
                    and passport_number != person_passport.number
                ):
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

                self.mapper.apply_passport_update_to_orm(passport, person_passport)

        await self.repo.update(person)
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
