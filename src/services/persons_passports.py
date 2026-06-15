from src.mappers.persons_passports import map_person_to_read, map_persons_paginated_list
from src.repositories.person import PersonRepository
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    def __init__(self, repo: PersonRepository):
        self.repo = repo

    async def create_person_with_passport(self, data: PersonCreate) -> None:
        passport = await self.repo.get_passport_by_number(data.passport.number)
        if passport is not None:
            self._raise_already_exists(
                message="A person with this passport number already exists",
            )
        person = await self.repo.create_person_with_passport(
            first_name=data.first_name,
            last_name=data.last_name,
            passport_number=data.passport.number,
            registrated_in=data.passport.registrated_in,
        )
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=person.passport.id,
        )

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.repo.get_person_with_passport(person_id)
        if person is None:
            self._raise_not_found(
                message="Person not found",
                person_id=person_id,
            )
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
        person = await self.repo.delete_person_with_passport(person_id)
        if person is None:
            self._raise_not_found(
                message="Person not found",
                person_id=person_id,
            )
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update_person_with_passport(self, person_id: int, data: PersonUpdate) -> None:
        person = await self.repo.get_person_with_passport(person_id)
        if person is None:
            self._raise_not_found(
                message="Person not found",
                person_id=person_id,
            )

        person_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"passport"},
        )
        passport_data = {}
        if data.passport is not None and data.passport.number is not None:
            passport = await self.repo.get_passport_by_number(data.passport.number)
            if passport is not None and passport.person_id != person_id:
                self._raise_already_exists(
                    message="A person with this passport number already exists",
                )
        if data.passport is not None:
            passport_data = data.passport.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )
        person = await self.repo.update_person_with_passport(
            person_id,
            person_data,
            passport_data,
        )
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
