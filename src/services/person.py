from src.models.persons import PersonsOrm
from src.repositories.person import PersonRepository
from src.schemas.persons import PersonAdd, PersonAddRequest, PersonPatch
from src.services.base import BaseService


class PersonService(BaseService):
    person_not_found_msg = "Person not found"

    def __init__(self, repo: PersonRepository):
        self.repo = repo

    async def get_active_by_id_or_raise(self, person_id: int) -> PersonsOrm:
        person = await self.repo.get_by_id_active(person_id)
        if person is None:
            self._raise_not_found(
                message=self.person_not_found_msg,
                person_id=person_id,
            )
        return person

    async def get_page(self, limit: int, offset: int) -> tuple[list[PersonsOrm], int]:
        return await self.repo.get_page(limit, offset)

    async def create(self, data: PersonAdd | PersonAddRequest) -> PersonsOrm:
        return await self.repo.insert(
            first_name=data.first_name,
            last_name=data.last_name,
        )

    async def update(self, person_id: int, data: PersonPatch) -> None:
        await self.get_active_by_id_or_raise(person_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"passport"},
        )
        if not values:
            return
        await self.repo.update(person_id, values)

    async def soft_delete(self, person_id: int) -> None:
        await self.get_active_by_id_or_raise(person_id)
        await self.repo.soft_delete(person_id)
