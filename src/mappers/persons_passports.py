from typing import Sequence

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
    def map_person_update_to_orm(
        self,
        data: PersonUpdate,
    ) -> PersonsOrm:
        return PersonsOrm(
            **data.model_dump(
                exclude={"passport"},
                exclude_none=True,
                exclude_unset=True,
            )
        )

    def map_passport_update_to_orm(
        self,
        data: PassportUpdate,
    ) -> PassportsOrm:
        return PassportsOrm(
            **data.model_dump(
                exclude_none=True,
                exclude_unset=True,
            )
        )

    def map_person_create_to_orm(self, data: PersonCreate) -> PersonsOrm:
        return PersonsOrm(
            **data.model_dump(exclude={"passport"}),
            passport=PassportsOrm(**data.passport.model_dump()),
        )

    def map_person_create_to_orm_without_passport(
        self,
        data: PersonCreate,
    ) -> PersonsOrm:
        return PersonsOrm(**data.model_dump(exclude={"passport"}))

    def map_passport_create_to_orm(
        self,
        *,
        person_id: int,
        data: PassportCreate,
    ) -> PassportsOrm:
        return PassportsOrm(
            person_id=person_id,
            **data.model_dump(),
        )

    def map_passport_to_read(self, passport: PassportsOrm) -> Passport:
        return Passport.model_validate(passport)

    def map_person_to_read(self, person: PersonsOrm) -> Person:
        return Person(
            **Person.model_validate(
                person,
                from_attributes=True,
            ).model_dump(exclude={"passport"}),
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
