from src.exceptions.authors_books import (
    AuthorAlreadyExistsException,
    AuthorNotFoundException,
    BookAlreadyExistsException,
)
from src.mappers.authors_books import (
    map_author_create_to_orm,
    map_author_update_books,
    map_author_update_to_values,
    map_author_to_read,
    map_authors_paginated_list,
    map_book_update_to_orm,
    map_book_update_to_values,
)
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

    async def create(self, data: AuthorCreate) -> Author:
        existing_author = await self.repo.get(author_code=data.author_code)
        if existing_author is not None:
            raise AuthorAlreadyExistsException(author_code=data.author_code)

        book_codes = [book.book_code for book in data.books]
        existing_books = await self.repo.get_books_by_codes(book_codes)
        if existing_books:
            conflicting_book_code = existing_books[0].book_code
            raise BookAlreadyExistsException(book_code=conflicting_book_code)

        author = await self.repo.create(map_author_create_to_orm(data))
        self.logger.info("author_created", author_id=author.id)
        return map_author_to_read(author)

    async def get(self, author_id: int) -> Author:
        author = await self.repo.get(id=author_id)
        if author is None:
            raise AuthorNotFoundException(author_id=author_id)
        return map_author_to_read(author)

    async def get_paginated_list(
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

    async def delete(self, author_id: int) -> None:
        author = await self.repo.get(id=author_id)
        if author is None:
            raise AuthorNotFoundException(author_id=author_id)
        for book in list(author.books):
            await self.repo.delete_book(book)
        await self.repo.delete(author)
        self.logger.info("author_deleted", author_id=author.id)

    async def update(self, author_id: int, data: AuthorUpdate) -> None:
        author = await self.repo.get(id=author_id)
        if author is None:
            raise AuthorNotFoundException(author_id=author_id)

        author_payload = map_author_update_to_values(data)
        books_payload = map_author_update_books(data)

        # проверяем поля автора
        author_code = author_payload.get("author_code")
        if author_code is not None:
            existing_author = await self.repo.get(author_code=author_code)
            if existing_author is not None and existing_author.id != author_id:
                raise AuthorAlreadyExistsException(author_code=author_code)

        if books_payload is not None:
            book_codes = [book.book_code for book in books_payload]

            conflicting_book_code = None
            existing_books = await self.repo.get_books_by_codes(book_codes)
            for book in existing_books:
                if book.author_id == author_id:
                    continue
                conflicting_book_code = book.book_code
                break

            if conflicting_book_code is not None:
                raise BookAlreadyExistsException(book_code=conflicting_book_code)

        if author_payload:
            await self.repo.update(author, author_payload)

        # обновляем список книг автора
        if books_payload is not None:
            existing_books_by_code = {book.book_code: book for book in author.books}
            target_codes = {book_data.book_code for book_data in books_payload}

            for book_data in books_payload:
                existing_book = existing_books_by_code.get(book_data.book_code)
                if existing_book is None:
                    await self.repo.create_book(
                        map_book_update_to_orm(author.id, book_data)
                    )
                    continue
                await self.repo.update_book(
                    existing_book,
                    map_book_update_to_values(book_data),
                )

            for book in list(author.books):
                if book.book_code not in target_codes:
                    await self.repo.delete_book(book)

        self.logger.info("author_updated", author_id=author.id)
