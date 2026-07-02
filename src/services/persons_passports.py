from src.mappers.persons_passports import (
    map_passport_update_to_values,
    map_person_create_to_orm,
    map_person_update_to_values,
    map_person_to_read,
    map_persons_paginated_list,
)
from src.repositories.person import PersonRepository
from src.schemas.errors import PassportErrorDetails, PersonErrorDetails
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
            self._raise_already_exists(
                message="A person with this passport number already exists",
                details=PassportErrorDetails(passport_number=data.passport.number),
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
            self._raise_not_found(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
                person_id=person_id,
            )
        return map_person_to_read(person)

    async def get_paginated_list(
        self, limit: int, offset: int
    ) -> PersonsPaginatedList:
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
            self._raise_not_found(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
                person_id=person_id,
            )
        await self.repo.delete_passport(person.passport)
        await self.repo.delete(person)
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update(self, person_id: int, data: PersonUpdate) -> None:
        person = await self.repo.get(id=person_id)
        if person is None:
            self._raise_not_found(
                message="Person not found",
                details=PersonErrorDetails(person_id=person_id),
                person_id=person_id,
            )

        person_payload = map_person_update_to_values(data)
        passport_payload = map_passport_update_to_values(data)

        if passport_payload is not None:
            passport_number = passport_payload.get("number")
            if passport_number is not None:
                existing_person = await self.repo.get_person_by_passport_number(
                    passport_number
                )
                if existing_person is not None and existing_person.id != person_id:
                    self._raise_already_exists(
                        message="A person with this passport number already exists",
                        details=PassportErrorDetails(
                            passport_number=passport_number
                        ),
                        passport_number=passport_number,
                    )

        if person_payload:
            await self.repo.update(person, person_payload)

        if passport_payload is not None:
            await self.repo.update_passport(
                person.passport,
                passport_payload,
            )

        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
