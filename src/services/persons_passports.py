from sqlalchemy.exc import IntegrityError

from src.exceptions.persons_passports import PassportAlreadyExistsException, PersonNotFoundException
from src.mappers.persons_passports import map_person_to_read, map_persons_paginated_list
from src.repositories.person import PersonRepository
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    def __init__(self, repo: PersonRepository):
        self.repo = repo

    def _raise_domain_error_from_integrity(self, exc: IntegrityError) -> None:
        self._raise_already_exists(
            PassportAlreadyExistsException,
            exc,
        )

    async def create_person_with_passport(self, data: PersonCreate) -> None:
        try:
            person = await self.repo.create_person_with_passport(data)
        except IntegrityError as exc:
            self._raise_domain_error_from_integrity(exc)
        if person is None:
            self._raise_not_found(PersonNotFoundException)
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=person.passport.id,
        )

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.repo.get_person_with_passport(person_id)
        if person is None:
            self._raise_not_found(
                PersonNotFoundException,
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
                PersonNotFoundException,
                person_id=person_id,
            )
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update_person_with_passport(self, person_id: int, data: PersonUpdate) -> None:
        try:
            person = await self.repo.update_person_with_passport(person_id, data)
        except IntegrityError as exc:
            self._raise_domain_error_from_integrity(exc)
        if person is None:
            self._raise_not_found(
                PersonNotFoundException,
                person_id=person_id,
            )
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=person.passport.id,
        )
