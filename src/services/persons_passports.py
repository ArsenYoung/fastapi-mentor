from sqlalchemy.exc import IntegrityError
from src.exceptions.passports import PassportConflictError, PassportNotFoundError
from src.exceptions.persons import PersonNotFoundError
from src.schemas.persons import Person, PersonAddRequest, PersonPage, PersonPatch


class PersonsPassportsService():
    def __init__(self, repo):
        self.repo = repo
    
    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        try:
            await self.repo.create_person_with_passport(data)
        except IntegrityError as exc:
            raise PassportConflictError from exc

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.repo.get_person_with_passport(person_id)
        if person is None:
            raise PersonNotFoundError()
        return person
    
    async def get_all_persons_with_passports(self, limit: int, offset: int) -> PersonPage:
        items, total = await self.repo.get_all_persons_with_passports(limit, offset)
        return PersonPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
    
    async def del_person_with_passport(self, person_id: int) -> None:
        is_deleted = await self.repo.del_person_with_passport(person_id)
        if not is_deleted:
            raise PersonNotFoundError()
        
    async def update_person_with_passport(self, person_id, data: PersonPatch) -> None:
        try:
            result = await self.repo.update_person_with_passport(person_id, data)
        except IntegrityError as exc:
            raise PassportConflictError()
        
        if not result.person_found:
            raise PersonNotFoundError()
        
        if not result.passport_found:
            raise PassportNotFoundError()
    
        
