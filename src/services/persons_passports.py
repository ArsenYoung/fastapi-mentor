from sqlalchemy.exc import IntegrityError
import structlog

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.repositories.persons_passports import PersonsPassportsRepository
from src.schemas.persons import Person, PersonAddRequest, PersonPage, PersonPatch
from src.services.base import BaseService


class PersonsPassportsService(BaseService):
    logger = structlog.get_logger()
    
    def __init__(self, repo: PersonsPassportsRepository):
        self.repo = repo

    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        try:
            person = await self.repo.insert_person(
                first_name=data.first_name,
                last_name=data.last_name,
            )
            passport = await self.repo.insert_passport(
                person_id=person.id,
                number=data.passport.number,
                registrated_in=data.passport.registrated_in,
            )
        except IntegrityError as exc:
            self.logger.warning(
                "person_already_exists",
                passport_number=data.passport.number,
            )
            raise AlreadyExistsException("A person with this passport number already exists") from exc
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=passport.id,
        )

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.repo.get_person(person_id)
        if person is None:
            self.logger.warning(
                "person_not_found",
                person_id=person_id,
            )
            raise ObjectNotFoundException("Person not found")

        passport = await self.repo.get_passport(person_id)
        if passport is None:
            self.logger.warning(
                "passport_not_found",
                person_id=person_id,
            )
            raise ObjectNotFoundException("Passport not found")

        person.passport = passport
        return Person.model_validate(person)

    async def get_all_persons_with_passports(self, limit: int, offset: int) -> PersonPage:
        persons, total = await self.repo.get_persons_page(limit, offset)
        items=[]
        if persons:
            person_ids = [person.id for person in persons]
        passports = await self.repo.get_passports_by_person_ids(person_ids)
        passports_by_person_id = {passport.person_id: passport for passport in passports}

        items: list[Person] = []
        for person in persons:
            passport = passports_by_person_id.get(person.id)
            if passport is None:
                continue
            person.passport = passport
            items.append(Person.model_validate(person))

        return PersonPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_person_with_passport(self, person_id: int) -> None:
        person = await self.repo.get_person(person_id)
        if person is None:
            self.logger.warning(
                "person_not_found",
                person_id=person_id,
            )
            raise ObjectNotFoundException("Person not found")

        await self.repo.soft_delete_person(person_id)
        await self.repo.soft_delete_passport(person_id)
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update_person_with_passport(self, person_id: int, data: PersonPatch) -> None:
        person = await self.repo.get_person(person_id)
        if person is None:
            self.logger.warning(
                "person_not_found",
                person_id=person_id,
            )
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
            self.logger.warning(
                "passport_not_found",
                person_id=person_id,
            )
            raise ObjectNotFoundException("Passport not found")

        passport_data = data.passport.model_dump(exclude_unset=True)
        if not passport_data:
            return

        try:
            await self.repo.update_passport(person_id, passport_data)
        except IntegrityError as exc:
            self.logger.warning(
                "person_already_exists",
                person_id=person.id,
                passport_number=passport_data.get("number", data.passport.number),
            )
            raise AlreadyExistsException("A person with this passport number already exists") from exc
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=passport.id,
        )
