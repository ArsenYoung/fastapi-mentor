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

    async def get_person(self, person_id: int) -> Person:
        person = await self.session.execute(
            select(PersonsOrm).filter_by(
                id=person_id,
                is_deleted=False
            ))
        person_response = person.scalar_one_or_none()
        return person_response

    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        person = PersonsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
        )
        self.session.add(person)
        await self.session.flush()

        passport = PassportsOrm(
            person_id=person.id,
            number=data.passport.number,
            registrated_in=data.passport.registrated_in,
        )
        self.session.add(passport)

    async def get_person_with_passport(self, person_id: int) -> Person | None:
        person = await self.get_person(person_id)

        if person is None:
            return None
        
        passport_response = await self.session.execute(
            select(PassportsOrm).filter_by(
                person_id=person.id
        ))
        passport = passport_response.scalar_one_or_none()
        return build_person_response(person, passport)


    async def del_person_with_passport(self, person_id: int) -> bool:
        person = await self.get_person(person_id)
        if person is None:
            return False
        await self.session.execute(
            update(PersonsOrm)
            .filter_by(id=person_id)
            .values(is_deleted=True)
        )
        await self.session.execute(
            update(PassportsOrm)
            .filter_by(person_id=person_id)
            .values(is_deleted=True)
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
            await self.session.execute(
                update(PersonsOrm)
                .filter_by(id=person_id)
                .values(**person_data)
            )

        if data.passport is not None:
            passport_result = await self.session.execute(
                select(PassportsOrm)
                .filter_by(
                    person_id=person_id,
                    is_deleted=False
                )
            )
            passport = passport_result.scalar_one_or_none()
            if passport is None:
                return UpdatePersonResult(
                    person_found=True,
                    passport_found=False
                )
            
            passport_data = data.passport.model_dump(exclude_unset=True)
            await self.session.execute(
                update(PassportsOrm)
                .filter_by(person_id=person_id)
                .values(**passport_data)
            )

        return UpdatePersonResult(
            person_found=True,
            passport_found=True
        )