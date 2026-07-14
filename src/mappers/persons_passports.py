from typing import Any, Sequence

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.schemas.passports import Passport
from src.schemas.passports import PassportCreate
from src.schemas.passports import PassportUpdate
from src.schemas.persons import (
    Person,
    PersonCreate,
    PersonsPaginatedList,
    PersonUpdate,
)


class PersonsPassportsMapper:
    def apply_person_update_to_orm(
        self,
        data: PersonUpdate,
        person: PersonsOrm,
    ) -> PersonsOrm:
        if data.first_name is not None:
            person.first_name = data.first_name
        if data.last_name is not None:
            person.last_name = data.last_name
        return person

    def apply_passport_update_to_orm(
        self,
        data: PassportUpdate,
        passport: PassportsOrm,
    ) -> PassportsOrm:
        if data.number is not None:
            passport.number = data.number
        if data.registrated_in is not None:
            passport.registrated_in = data.registrated_in
        return passport

    def map_person_create_to_orm(self, data: PersonCreate) -> PersonsOrm:
        return PersonsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
            passport=PassportsOrm(
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            ),
        )

    def map_person_create_to_orm_without_passport(
        self,
        data: PersonCreate,
    ) -> PersonsOrm:
        return PersonsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
        )

    def map_passport_create_to_insert_values(
        self,
        *,
        person_id: int,
        data: PassportCreate,
    ) -> dict[str, Any]:
        return {
            "person_id": person_id,
            "number": data.number,
            "registrated_in": data.registrated_in,
        }

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
