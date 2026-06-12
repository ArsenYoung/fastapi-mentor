from sqlalchemy.exc import IntegrityError

from src.models.authors import AuthorsOrm
from src.repositories.author import AuthorRepository
from src.schemas.authors import AuthorCreateRequest, AuthorPatch
from src.services.base import BaseService


class AuthorService(BaseService):
    author_not_found_msg = "Author not found"
    author_already_exists_msg = "An author with this code already exists"
    author_unique_constraint = "uq_authors_author_code_active"

    def __init__(self, repo: AuthorRepository):
        self.repo = repo

    def _is_author_unique_error(self, exc: IntegrityError) -> bool:
        return self.author_unique_constraint in str(exc)

    async def get_active_by_id_or_raise(self, author_id: int) -> AuthorsOrm:
        author = await self.repo.get_by_id_active(author_id)
        if author is None:
            self._raise_not_found(
                message=self.author_not_found_msg,
                author_id=author_id
            )
        return author

    async def get_any_by_code(self, author_code: str) -> AuthorsOrm | None:
        return await self.repo.get_any_by_author_code(author_code)
    
    async def get_page(self, limit: int, offset: int) -> tuple[list[AuthorsOrm], int]:
        return await self.repo.get_page(limit, offset)

    async def create(self, data: AuthorCreateRequest) -> AuthorsOrm:
        try:
            return await self.repo.insert(
                author_code=data.author_code,
                first_name=data.first_name,
                last_name=data.last_name,
            )
        except IntegrityError as exc:
            if self._is_author_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.author_already_exists_msg,
                    author_code=data.author_code,
                )
            raise

    async def create_or_restore(self, data: AuthorCreateRequest) -> AuthorsOrm:
        author = await self.get_any_by_code(data.author_code)
        if author is None:
            return await self.create(data)
        if author.is_deleted:
            await self.restore(author.id)
            await self.update(
                author.id,
                AuthorPatch(
                    author_code=data.author_code,
                    first_name=data.first_name,
                    last_name=data.last_name,
                )
            )
            return await self.get_active_by_id_or_raise(author.id)
        self._raise_already_exists(
            message=self.author_already_exists_msg,
            author_code=data.author_code,
        )

    async def update(self, author_id: int, data: AuthorPatch) -> None:
        await self.get_active_by_id_or_raise(author_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"books"},
        )
        if not values:
            return
        try:
            await self.repo.update(author_id, values)
        except IntegrityError as exc:
            if self._is_author_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.author_already_exists_msg,
                    author_id=author_id,
                    author_code=data.author_code,
                )
            raise

    async def soft_delete(self, author_id: int) -> None:
        await self.get_active_by_id_or_raise(author_id)
        await self.repo.soft_delete(author_id)

    async def restore(self, author_id: int) -> None:
        author = await self.repo.get_by_id_any(author_id)
        if author is None:
            self._raise_not_found(
               message=self.author_not_found_msg, 
               author_id=author_id
            )
        try:
            await self.repo.restore(author_id)
        except IntegrityError as exc:
            if self._is_author_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.author_already_exists_msg,
                    author_id=author_id,
                    author_code=author.author_code,
                )
            raise
