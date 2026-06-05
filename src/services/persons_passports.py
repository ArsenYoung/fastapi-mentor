from sqlalchemy.exc import IntegrityError

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.mappers.persons_passports import build_person_response
from src.repositories.persons_passports import PersonsPassportsRepository
from src.schemas.persons import Person, PersonAddRequest, PersonPage, PersonPatch


class PersonsPassportsService:
    def __init__(self, repo: PersonsPassportsRepository):
        self.repo = repo

    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        try:
            person = await self.repo.insert_person(
                first_name=data.first_name,
                last_name=data.last_name,
            )
            await self.repo.insert_passport(
                person_id=person.id,
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            )
        except IntegrityError as exc:
            raise AlreadyExistsException("A person with this passport number already exists") from exc

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.repo.get_person(person_id)
        if person is None:
            raise ObjectNotFoundException("Person not found")

        passport = await self.repo.get_passport(person_id)
        if passport is None:
            raise ObjectNotFoundException("Passport not found")

        return build_person_response(person, passport)

    async def get_all_persons_with_passports(self, limit: int, offset: int) -> PersonPage:
        persons, total = await self.repo.get_persons_page(limit, offset)
        items=[]
        if persons:
            person_ids = [person.id for person in persons]
            passports = await self.repo.get_passports_by_person_ids(person_ids)
            passports_by_person_id = {passport.person_id: passport for passport in passports}

            items = [
                build_person_response(person, passports_by_person_id[person.id])
                for person in persons
                if person.id in passports_by_person_id
            ]

        return PersonPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_person_with_passport(self, person_id: int) -> None:
        person = await self.repo.get_person(person_id)
        if person is None:
            raise ObjectNotFoundException("Person not found")

        await self.repo.soft_delete_person(person_id)
        await self.repo.soft_delete_passport(person_id)

    async def update_person_with_passport(self, person_id: int, data: PersonPatch) -> None:
        person = await self.repo.get_person(person_id)
        if person is None:
            raise ObjectNotFoundException("Person not found")

        person_data = data.model_dump(
            exclude_unset=True,
            exclude={"passport"},
        )
        if person_data:
            await self.repo.update_person(person_id, person_data)

        if data.passport is None:
            return

        passport = await self.repo.get_passport(person_id)
        if passport is None:
            raise ObjectNotFoundException("Passport not found")

        passport_data = data.passport.model_dump(exclude_unset=True)
        if not passport_data:
            return

        try:
            await self.repo.update_passport(person_id, passport_data)
        except IntegrityError as exc:
            raise AlreadyExistsException("A person with this passport number already exists") from exc
