from dataclasses import dataclass

from sqlalchemy import select, update

from src.mappers.persons_passports import build_person_response
from src.models.passports import PassportsOrm
from src.models.persons import PersonsOrm
from src.repositories.base import BaseRepository
from src.schemas.persons import Person, PersonAddRequest, PersonPatch

@dataclass(slots=True)
class UpdatePersonResult:
    person_found: bool
    passport_found: bool
    

class PersonsPassportsRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_person(self, person_id: int) -> Person | None:
        return await self.fetch_active_one(PersonsOrm, id=person_id)

    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        person = await self.insert_instance(
            PersonsOrm(
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )
        await self.insert_instance(
            PassportsOrm(
                person_id=person.id,
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            )
        )

    async def get_person_with_passport(self, person_id: int) -> Person | None:
        person = await self.get_person(person_id)
        if person is None:
            return None
        passport = await self.fetch_active_one(
            PassportsOrm,
            person_id=person.id,
        )
        return build_person_response(person, passport)


    async def del_person_with_passport(self, person_id: int) -> bool:
        person = await self.get_person(person_id)
        if person is None:
            return False
        await self.soft_delete_where(
            PersonsOrm,
            id=person_id,
        )
        await self.soft_delete_where(
            PassportsOrm,
            person_id=person_id,
        )
        return True

    async def update_person_with_passport(self, person_id: int, data: PersonPatch) -> None:
        person = await self.get_person(person_id)
        if person is None:
            return UpdatePersonResult(
                person_found=False,
                passport_found=False
            )
        person_data = data.model_dump(
            exclude_unset=True,
            exclude={"passport"},
        )
        if person_data:
            await self.update_where(
                PersonsOrm,
                person_data,
                id=person_id,
            )
        if data.passport is not None:
            passport = await self.fetch_active_one(
                PassportsOrm,
                person_id=person_id,
            )
            if passport is None:
                return UpdatePersonResult(
                    person_found=True,
                    passport_found=False
                )
            await self.update_where(
                PassportsOrm,
                data.passport.model_dump(exclude_unset=True),
                person_id=person_id,
            )
        return UpdatePersonResult(
            person_found=True,
            passport_found=True
        )