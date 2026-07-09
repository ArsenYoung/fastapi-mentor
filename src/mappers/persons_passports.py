from typing import Any, Sequence

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.schemas.passports import Passport
from src.schemas.passports import PassportUpdate
from src.schemas.persons import (
    Person,
    PersonCreate,
    PersonsPaginatedList,
    PersonUpdate,
)


class PersonsPassportsMapper:
    def map_person_update_to_fields(
        self,
        data: PersonUpdate,
    ) -> dict[str, Any]:
        return data.model_dump(
            exclude_none=True,
            exclude={"passport"},
        )

    def map_passport_update_to_fields(
        self,
        data: PassportUpdate,
    ) -> dict[str, Any]:
        return data.model_dump(exclude_none=True)

    def map_person_create_to_orm(self, data: PersonCreate) -> PersonsOrm:
        return PersonsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
            passport=PassportsOrm(
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            ),
        )

    def map_passport_to_read(self, passport: PassportsOrm) -> Passport:
        return Passport(
            id=passport.id,
            number=passport.number,
            registrated_in=passport.registrated_in,
        )

    def map_person_to_read(self, person: PersonsOrm) -> Person:
        return Person(
            id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            passport=self.map_passport_to_read(person.passport),
        )

    def map_persons_paginated_list(
        self,
        persons: Sequence[PersonsOrm],
        *,
        has_next: bool,
        limit: int,
        offset: int,
    ) -> PersonsPaginatedList:
        return PersonsPaginatedList(
            items=[self.map_person_to_read(person) for person in persons],
            has_next=has_next,
            limit=limit,
            offset=offset,
        )
