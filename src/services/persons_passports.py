from src.schemas.persons import Person, PersonAddRequest, PersonPage, PersonPatch
from src.services.passport import PassportService
from src.services.base import BaseService
from src.services.person import PersonService


class PersonsPassportsService(BaseService):
    def __init__(
        self,
        person_service: PersonService,
        passport_service: PassportService,
    ):
        self.person_service = person_service
        self.passport_service = passport_service

    async def create_person_with_passport(self, data: PersonAddRequest) -> None:
        person = await self.person_service.create(data)
        passport = await self.passport_service.create(person.id, data.passport)
        self.logger.info(
            "person_created",
            person_id=person.id,
            passport_id=passport.id,
        )

    async def get_person_with_passport(self, person_id: int) -> Person:
        person = await self.person_service.get_active_by_id_or_raise(person_id)
        passport = await self.passport_service.get_read_by_person_id(person_id)
        return Person(
            id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            passport=passport,
        )

    async def get_all_persons_with_passports(self, limit: int, offset: int) -> PersonPage:
        persons, total = await self.person_service.get_page(limit, offset)
        if not persons:
            return PersonPage(
                items=[],
                total=total,
                limit=limit,
                offset=offset,
            )

        person_ids = [person.id for person in persons]
        passports = await self.passport_service.get_by_person_ids(person_ids)
        passports_by_person_id = {passport.person_id: passport for passport in passports}

        items: list[Person] = []
        for person in persons:
            passport = passports_by_person_id.get(person.id)
            if passport is None:
                continue
            items.append(
                Person(
                    id=person.id,
                    first_name=person.first_name,
                    last_name=person.last_name,
                    passport={
                        "id": passport.id,
                        "number": passport.number,
                        "registrated_in": passport.registrated_in,
                    },
                )
            )

        return PersonPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_person_with_passport(self, person_id: int) -> None:
        person = await self.person_service.get_active_by_id_or_raise(person_id)
        await self.passport_service.soft_delete_by_person_id(person_id)
        await self.person_service.soft_delete(person_id)
        self.logger.info(
            "person_deleted",
            person_id=person.id,
        )

    async def update_person_with_passport(self, person_id: int, data: PersonPatch) -> None:
        person = await self.person_service.get_active_by_id_or_raise(person_id)
        person_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"passport"},
        )
        if person_data:
            await self.person_service.update(person_id, data)

        if data.passport is None:
            return

        passport = await self.passport_service.get_by_person_id_or_raise(person_id)
        await self.passport_service.update_by_person_id(person_id, data.passport)
        self.logger.info(
            "person_updated",
            person_id=person.id,
            passport_id=passport.id,
        )
