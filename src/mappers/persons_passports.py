from typing import Dict, List

from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.schemas.passports import Passport, PassportCreate, PassportUpdate
from src.schemas.persons import Person, PersonCreate, PersonsPaginatedList, PersonUpdate


def map_person_create_to_person_payload(data: PersonCreate) -> Dict[str, str]:
    return data.model_dump(
        exclude={"passport"},
    )


def map_person_update_to_person_payload(data: PersonUpdate) -> Dict[str, str]:
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude={"passport"},
    )


def map_passport_create_to_orm(data: PassportCreate, person_id: int) -> PassportsOrm:
    return PassportsOrm(
        person_id=person_id,
        number=data.number,
        registrated_in=data.registrated_in,
    )


def map_passport_update_to_payload(data: PassportUpdate | None) -> Dict[str, str]:
    if data is None:
        return {}
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )


def map_passport_to_read(passport: PassportsOrm) -> Passport:
    return Passport(
        id=passport.id,
        number=passport.number,
        registrated_in=passport.registrated_in,
    )


def map_person_to_read(person: PersonsOrm) -> Person:
    return Person(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        passport=map_passport_to_read(person.passport),
    )


def map_persons_paginated_list(
    persons: List[PersonsOrm],
    *,
    has_next: bool,
    limit: int,
    offset: int,
) -> PersonsPaginatedList:
    return PersonsPaginatedList(
        items=[
            map_person_to_read(person)
            for person in persons
            if person.passport is not None
        ],
        has_next=has_next,
        limit=limit,
        offset=offset,
    )
