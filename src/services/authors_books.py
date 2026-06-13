from sqlalchemy.exc import IntegrityError

from src.exceptions.authors_books import (
    AuthorAlreadyExistsException,
    AuthorNotFoundException,
    BookAlreadyExistsException,
)
from src.mappers.authors_books import map_author_to_read, map_authors_paginated_list
from src.repositories.author import AuthorRepository
from src.schemas.authors import (
    Author,
    AuthorCreate,
    AuthorsPaginatedList,
    AuthorUpdate,
)
from src.services.base import BaseService

AUTHOR_CONSTRAINT_ERRORS = {
    "uq_authors_author_code_active": AuthorAlreadyExistsException,
    "uq_books_book_code_active": BookAlreadyExistsException,
}


class AuthorsBooksService(BaseService):
    def __init__(self, repo: AuthorRepository):
        self.repo = repo

    def _raise_if_duplicate_book_codes(self, book_codes: list[str], *, author_id: int | None = None) -> None:
        seen_codes: set[str] = set()
        for book_code in book_codes:
            if book_code in seen_codes:
                self._raise_already_exists(
                    BookAlreadyExistsException,
                    author_id=author_id,
                    book_code=book_code,
                )
            seen_codes.add(book_code)

    def _raise_domain_error_from_integrity(self, exc: IntegrityError) -> None:
        self._raise_mapped_integrity_error(exc, AUTHOR_CONSTRAINT_ERRORS)

    async def create_author_with_books(self, data: AuthorCreate) -> None:
        self._raise_if_duplicate_book_codes([book.book_code for book in data.books])
        try:
            author = await self.repo.create_author_with_books(data)
        except IntegrityError as exc:
            self._raise_domain_error_from_integrity(exc)
        if author is None:
            self._raise_not_found(AuthorNotFoundException)
        self.logger.info("author_created", author_id=author.id)

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get_author_with_books(author_id)
        if author is None:
            self._raise_not_found(
                AuthorNotFoundException,
                author_id=author_id,
            )
        return map_author_to_read(author)

    async def get_authors_with_books_paginated_list(self, limit: int, offset: int) -> AuthorsPaginatedList:
        authors, has_next = await self.repo.get_authors_with_books_paginated_list(
            limit,
            offset,
        )
        return map_authors_paginated_list(
            authors,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete_author_with_books(self, author_id: int) -> None:
        author = await self.repo.delete_author_with_books(author_id)
        if author is None:
            self._raise_not_found(
                AuthorNotFoundException,
                author_id=author_id,
            )
        self.logger.info("author_deleted", author_id=author.id)

    async def update_author_with_books(self, author_id: int, data: AuthorUpdate) -> None:
        if data.books is not None:
            self._raise_if_duplicate_book_codes(
                [book.book_code for book in data.books],
                author_id=author_id,
            )
        try:
            author = await self.repo.update_author_with_books(author_id, data)
        except IntegrityError as exc:
            self._raise_domain_error_from_integrity(exc)
        if author is None:
            self._raise_not_found(
                AuthorNotFoundException,
                author_id=author_id,
            )
        self.logger.info("author_updated", author_id=author.id)
