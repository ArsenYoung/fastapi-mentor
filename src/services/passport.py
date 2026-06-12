from sqlalchemy.exc import IntegrityError

from src.models.passports import PassportsOrm
from src.repositories.passport import PassportRepository
from src.schemas.passports import Passport, PassportAddRequest, PassportPatch
from src.services.base import BaseService


class PassportService(BaseService):
    passport_not_found_msg = "Passport not found"
    passport_already_exists_msg = "A person with this passport number already exists"

    def __init__(self, repo: PassportRepository):
        self.repo = repo

    async def get_by_person_id_or_raise(self, person_id: int) -> PassportsOrm:
        passport = await self.repo.get_by_person_id_active(person_id)
        if passport is None:
            self._raise_not_found(
                message=self.passport_not_found_msg,
                person_id=person_id,
            )
        return passport

    async def get_by_person_ids(self, person_ids: list[int]) -> list[PassportsOrm]:
        return await self.repo.get_by_person_ids(person_ids)

    async def create(self, person_id: int, data: PassportAddRequest) -> PassportsOrm:
        try:
            return await self.repo.insert(
                person_id=person_id,
                number=data.number,
                registrated_in=data.registrated_in,
            )
        except IntegrityError as exc:
            self._raise_already_exists(
                exc,
                message=self.passport_already_exists_msg,
                person_id=person_id,
                passport_number=data.number,
            )

    async def get_read_by_person_id(self, person_id: int) -> Passport:
        passport = await self.get_by_person_id_or_raise(person_id)
        return Passport.model_validate(passport)

    async def update_by_person_id(self, person_id: int, data: PassportPatch) -> None:
        await self.get_by_person_id_or_raise(person_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        if not values:
            return
        try:
            await self.repo.update_by_person_id(person_id, values)
        except IntegrityError as exc:
            self._raise_already_exists(
                exc,
                message=self.passport_already_exists_msg,
                person_id=person_id,
                passport_number=values.get("number"),
            )

    async def soft_delete_by_person_id(self, person_id: int) -> None:
        await self.get_by_person_id_or_raise(person_id)
        await self.repo.soft_delete_by_person_id(person_id)
