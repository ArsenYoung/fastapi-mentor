from typing import List, Mapping, Sequence, Set, Tuple

from src.mappers.authors_books import (
    map_author_to_read,
    map_authors_paginated_list,
    map_book_payload_to_orm,
)
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
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
            details={"author_code": author_code},
            author_code=author_code,
        )

    def _raise_if_author_not_found(self, author: AuthorsOrm | None, author_id: int) -> AuthorsOrm:
        if author is None:
            self._raise_not_found(
                message="Author not found",
                details={"author_id": author_id},
                author_id=author_id,
            )
        return author

    def _raise_if_duplicate_book_codes(self, book_codes: Sequence[str], *, author_id: int | None = None) -> None:
        seen_codes: Set[str] = set()
        for book_code in book_codes:
            if book_code in seen_codes:
                self._raise_already_exists(
                    message="A book with this code already exists",
                    details={"book_code": book_code},
                    author_id=author_id,
                    book_code=book_code,
                )
            seen_codes.add(book_code)

    async def _raise_if_book_codes_exist(
        self,
        book_codes: Sequence[str],
        *,
        exclude_author_id: int | None = None,
        author_id: int | None = None,
    ) -> None:
        target_book_codes = set(book_codes)
        authors = await self.repo.get_authors_by_book_codes(book_codes)
        for author in authors:
            for book in author.books:
                if book.book_code not in target_book_codes:
                    continue
                if (
                    exclude_author_id is not None
                    and author.id == exclude_author_id
                    and not book.is_deleted
                ):
                    continue
                self._raise_already_exists(
                    message="A book with this code already exists",
                    details={"book_code": book.book_code},
                    author_id=author_id,
                    book_code=book.book_code,
                )

    def _get_author_book_changes(
        self,
        author: AuthorsOrm,
        books_data: Sequence[Mapping[str, str]],
    ) -> Tuple[List[Mapping[str, str]], List[Tuple[BooksOrm, str]], List[BooksOrm]]:
        existing_books_by_code = {
            book.book_code: book
            for book in author.books
        }
        target_codes = {book_data["book_code"] for book_data in books_data}
        books_to_create = []
        books_to_update = []

        for book_data in books_data:
            existing_book = existing_books_by_code.get(book_data["book_code"])
            if existing_book is None:
                books_to_create.append(book_data)
                continue
            books_to_update.append((existing_book, book_data["title"]))

        books_to_delete = [
            book
            for book in author.books
            if book.book_code not in target_codes
        ]
        return books_to_create, books_to_update, books_to_delete

    async def _apply_author_book_changes(
        self,
        author: AuthorsOrm,
        books_to_create: Sequence[Mapping[str, str]],
        books_to_update: Sequence[Tuple[BooksOrm, str]],
        books_to_delete: Sequence[BooksOrm],
    ) -> None:
        author.books.extend(
            map_book_payload_to_orm(author.id, book_data)
            for book_data in books_to_create
        )
        for book, title in books_to_update:
            book.title = title
            book.is_deleted = False
        for book in books_to_delete:
            book.is_deleted = True
        await self.repo.flush()

    async def create_author_with_books(self, data: AuthorCreate) -> None:
        await self._raise_if_author_code_exists(data.author_code)
        self._raise_if_duplicate_book_codes([book.book_code for book in data.books])
        await self._raise_if_book_codes_exist([book.book_code for book in data.books])
        author = await self.repo.create_author_with_books(
            author_data=data.model_dump(exclude={"books"}),
            books_data=[book.model_dump() for book in data.books],
        )
        self.logger.info("author_created", author_id=author.id)

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get_author_with_books(author_id)
        author = self._raise_if_author_not_found(author, author_id)
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
        author = await self.repo.get_author_with_books(author_id)
        author = self._raise_if_author_not_found(author, author_id)
        for book in author.books:
            book.is_deleted = True
        await self.repo.delete(author.id)
        await self.repo.flush()
        self.logger.info("author_deleted", author_id=author.id)

    async def update_author_with_books(self, author_id: int, data: AuthorUpdate) -> None:
        author = await self.repo.get_author_with_books(author_id)
        author = self._raise_if_author_not_found(author, author_id)
        author_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"books"},
        )
        books_payload = (
            [book.model_dump() for book in data.books]
            if data.books is not None
            else None
        )
        book_codes = [book["book_code"] for book in books_payload] if books_payload is not None else None

        if data.author_code is not None:
            await self._raise_if_author_code_exists(
                data.author_code,
                exclude_author_id=author_id,
            )
        if book_codes is not None:
            self._raise_if_duplicate_book_codes(
                book_codes,
                author_id=author_id,
            )
            await self._raise_if_book_codes_exist(
                book_codes,
                exclude_author_id=author_id,
                author_id=author_id,
            )

        for field, value in author_data.items():
            setattr(author, field, value)
        if books_payload is not None:
            await self._apply_author_book_changes(
                author,
                *self._get_author_book_changes(
                    author,
                    books_payload,
                ),
            )
        elif author_data:
            await self.repo.flush()
        self.logger.info("author_updated", author_id=author.id)
