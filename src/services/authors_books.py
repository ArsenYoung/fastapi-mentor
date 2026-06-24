from src.mappers.authors_books import (
    map_author_payload_to_orm,
    map_author_to_read,
    map_authors_paginated_list,
    map_book_payload_to_orm,
)
from src.models.books import BooksOrm
from src.repositories.author import AuthorRepository
from src.schemas.authors import (
    Author,
    AuthorCreate,
    AuthorsPaginatedList,
    AuthorUpdate,
)
from src.schemas.books import BookUpdate
from src.schemas.errors import AuthorErrorDetails, BookErrorDetails
from src.services.base import BaseService


class AuthorsBooksService(BaseService):
    def __init__(self, repo: AuthorRepository):
        self.repo = repo

    async def create_author_with_books(self, data: AuthorCreate) -> Author:
        existing_author = await self.repo.get(author_code=data.author_code)
        if existing_author is not None:
            self._raise_already_exists(
                message="An author with this code already exists",
                details=AuthorErrorDetails(author_code=data.author_code),
                author_code=data.author_code,
            )

        # проверка что в боди нет книг с одним и тем же кодом
        book_codes = [book.book_code for book in data.books]
        seen_codes = set()
        conflicting_book_code = None
        for book_code in book_codes:
            if book_code in seen_codes:
                conflicting_book_code = book_code
                break
            seen_codes.add(book_code)

        # проверка на существование книг в БД
        if conflicting_book_code is None:
            existing_books = await self.repo.get_books_by_codes(book_codes)
            if existing_books:
                conflicting_book_code = existing_books[0].book_code

        if conflicting_book_code is not None:
            self._raise_already_exists(
                message="A book with this code already exists",
                details=BookErrorDetails(book_code=conflicting_book_code),
                book_code=conflicting_book_code,
            )

        author = await self.repo.create(
            map_author_payload_to_orm(
                data.model_dump(exclude={"books"}),
                [book.model_dump() for book in data.books],
            ),
        )
        self.logger.info("author_created", author_id=author.id)
        return map_author_to_read(author)

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get(author_id)
        if author is None:
            self._raise_not_found(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
                author_id=author_id,
            )
        return map_author_to_read(author)

    async def get_authors_with_books_paginated_list(
        self, limit: int, offset: int
    ) -> AuthorsPaginatedList:
        authors, has_next = await self.repo.get_paginated_list(
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
        author = await self.repo.get(author_id)
        if author is None:
            self._raise_not_found(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
                author_id=author_id,
            )
        for book in author.books:
            await self.repo.delete(book.id, model=BooksOrm)
        await self.repo.delete(author.id)
        self.logger.info("author_deleted", author_id=author.id)

    async def update_author_with_books(
        self, author_id: int, data: AuthorUpdate
    ) -> None:
        author = await self.repo.get(author_id)
        if author is None:
            self._raise_not_found(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
                author_id=author_id,
            )

        author_payload = data.model_dump(exclude_unset=True, exclude_none=True)
        books_payload = author_payload.pop("books", None)

        # проверяем поля автора
        author_code = author_payload.get("author_code")
        if author_code is not None:
            existing_author = await self.repo.get(author_code=author_code)
            if existing_author is not None and existing_author.id != author_id:
                self._raise_already_exists(
                    message="An author with this code already exists",
                    details=AuthorErrorDetails(author_code=author_code),
                    author_code=author_code,
                )

        # проверяем книги до любых изменений в БД
        if books_payload is not None:
            book_codes = [book["book_code"] for book in books_payload]

            seen_codes = set()
            conflicting_book_code = None
            for book_code in book_codes:
                if book_code in seen_codes:
                    conflicting_book_code = book_code
                    break
                seen_codes.add(book_code)

            if conflicting_book_code is None:
                existing_books = await self.repo.get_books_by_codes(book_codes)
                for book in existing_books:
                    if book.author_id == author_id:
                        continue
                    conflicting_book_code = book.book_code
                    break

            if conflicting_book_code is not None:
                self._raise_already_exists(
                    message="A book with this code already exists",
                    details=BookErrorDetails(book_code=conflicting_book_code),
                    author_id=author_id,
                    book_code=conflicting_book_code,
                )

        if author_payload:
            await self.repo.update(author_id, author_payload)

        # обновляем список книг автора
        if books_payload is not None:
            existing_books_by_code = {book.book_code: book for book in author.books}
            target_codes = {book_data["book_code"] for book_data in books_payload}

            for book_data in books_payload:
                existing_book = existing_books_by_code.get(book_data["book_code"])
                if existing_book is None:
                    await self.repo.create(
                        map_book_payload_to_orm(author.id, book_data)
                    )
                    continue
                await self.repo.update(
                    existing_book.id,
                    BookUpdate(
                        title=book_data["title"],
                        is_deleted=False,
                    ).model_dump(exclude_none=True),
                    model=BooksOrm,
                )

            for book in author.books:
                if book.book_code not in target_codes:
                    await self.repo.delete(book.id, model=BooksOrm)

        self.logger.info("author_updated", author_id=author.id)
