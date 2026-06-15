from src.mappers.authors_books import map_author_to_read, map_authors_paginated_list
from src.repositories.author import AuthorRepository
from src.schemas.authors import (
    Author,
    AuthorCreate,
    AuthorsPaginatedList,
    AuthorUpdate,
)
from src.services.base import BaseService


class AuthorsBooksService(BaseService):
    def __init__(self, repo: AuthorRepository):
        self.repo = repo

    async def _raise_if_author_code_exists(
        self,
        author_code: str,
        *,
        exclude_author_id: int | None = None,
    ) -> None:
        author = await self.repo.get_author_by_code(author_code)
        if author is None or author.id == exclude_author_id:
            return
        self._raise_already_exists(
            message="An author with this code already exists",
            author_code=author_code,
        )

    def _raise_if_duplicate_book_codes(self, book_codes: list[str], *, author_id: int | None = None) -> None:
        seen_codes: set[str] = set()
        for book_code in book_codes:
            if book_code in seen_codes:
                self._raise_already_exists(
                    message="A book with this code already exists",
                    author_id=author_id,
                    book_code=book_code,
                )
            seen_codes.add(book_code)

    async def _raise_if_book_codes_exist(
        self,
        book_codes: list[str],
        *,
        exclude_author_id: int | None = None,
        author_id: int | None = None,
    ) -> None:
        existing_books = await self.repo.get_books_by_book_codes(book_codes)
        for book in existing_books:
            if book.author_id == exclude_author_id:
                continue
            self._raise_already_exists(
                message="A book with this code already exists",
                author_id=author_id,
                book_code=book.book_code,
            )

    async def create_author_with_books(self, data: AuthorCreate) -> None:
        await self._raise_if_author_code_exists(data.author_code)
        self._raise_if_duplicate_book_codes([book.book_code for book in data.books])
        await self._raise_if_book_codes_exist([book.book_code for book in data.books])
        author = await self.repo.create_author_with_books(
            author_code=data.author_code,
            first_name=data.first_name,
            last_name=data.last_name,
            books=[
                {
                    "book_code": book.book_code,
                    "title": book.title,
                }
                for book in data.books
            ],
        )
        self.logger.info("author_created", author_id=author.id)

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get_author_with_books(author_id)
        if author is None:
            self._raise_not_found(
                message="Author not found",
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
                message="Author not found",
                author_id=author_id,
            )
        self.logger.info("author_deleted", author_id=author.id)

    async def update_author_with_books(self, author_id: int, data: AuthorUpdate) -> None:
        author = await self.repo.get_author_with_books(author_id)
        if author is None:
            self._raise_not_found(
                message="Author not found",
                author_id=author_id,
            )
        author_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"books"},
        )
        books_data = None
        if data.author_code is not None:
            await self._raise_if_author_code_exists(
                data.author_code,
                exclude_author_id=author_id,
            )
        if data.books is not None:
            self._raise_if_duplicate_book_codes(
                [book.book_code for book in data.books],
                author_id=author_id,
            )
            await self._raise_if_book_codes_exist(
                [book.book_code for book in data.books],
                exclude_author_id=author_id,
                author_id=author_id,
            )
            books_data = [
                {
                    "book_code": book.book_code,
                    "title": book.title,
                }
                for book in data.books
            ]
        author = await self.repo.update_author_with_books(
            author_id,
            author_data,
            books_data,
        )
        self.logger.info("author_updated", author_id=author.id)
