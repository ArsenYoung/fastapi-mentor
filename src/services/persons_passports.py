from src.exceptions import PassportConflictError, PersonNotFoundError
from src.mappers.persons_passports import build_person_response
from src.repositories.passports import PassportsRepository
from src.repositories.persons import PersonsRepository
from src.schemas.passports import PassportAdd
from src.schemas.persons import Person, PersonAddRequest, PersonPatch


class PersonsPassportsService():
    def __init__(self, session):
        self.persons_repo = PersonsRepository(session)
        self.passports_repo = PassportsRepository(session)

    async def _get_person(self, **filter_by) -> Person:
        person = await self.persons_repo.get_one_or_none(**filter_by)
        if person is None:
            raise PersonNotFoundError()
        return person
    
    async def _check_passport_exist(self, **filter_by) -> None:
        passport = await self.passports_repo.get_one_or_none(**filter_by)
        if passport:
            raise PassportConflictError()
    
    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        await self._check_passport_exist(number=data.passport.number)
        person_response = await self.persons_repo.add(data, exclude={"passport"})
        passport_data = PassportAdd(
            number=data.passport.number,
            registrated_in=data.passport.registrated_in,
            person_id=person_response.id
        )
        await self.passports_repo.add(passport_data)

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self._get_person(id=person_id)
        passport = await self.passports_repo.get_one_or_none(person_id=person_id)
        return build_person_response(person, passport)
    
    async def del_person_with_passport(self, person_id: int) -> None:
        await self._get_person(id=person_id)
        await self.persons_repo.delete(id=person_id)
        await self.passports_repo.delete(person_id=person_id)
        
    async def update_person_with_passport(self, person_id, data: PersonPatch) -> None:
        await self._get_person(id=person_id)
        person_data = data.model_dump(
            exclude_unset=True,
            exclude={"passport"},
        )
        
        if person_data:
            await self.persons_repo.update(person_data, id=person_id)
        if data.passport:
            if data.passport.number is not None:
                await self._check_passport_exist(number=data.passport.number)
            passport_data = data.passport.model_dump(exclude_unset=True)
            await self.passports_repo.update(passport_data, person_id=person_id)
    
        
