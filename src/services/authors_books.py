from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.mappers.authors_books import AuthorsBooksMapper
from src.repositories.author import AuthorRepository
from src.schemas.authors import (
    Author,
    AuthorCreate,
    AuthorsPaginatedList,
    AuthorUpdate,
)
from src.schemas.errors import AuthorErrorDetails, BookErrorDetails
from src.services.base import BaseService


class AuthorsBooksService(BaseService):
    def __init__(self, repo: AuthorRepository, mapper: AuthorsBooksMapper):
        self.repo = repo
        self.mapper = mapper

    async def create(self, data: AuthorCreate) -> Author:
        author = await self.repo.create_do_nothing(
            self.mapper.map_author_create_to_insert_values(data),
        )
        if author is None:
            raise AlreadyExistsException(
                message="An author with this code already exists",
                details=AuthorErrorDetails(author_code=data.author_code),
            )

        await self.repo.create_books_do_nothing(
            self.mapper.map_book_creates_to_insert_values(author.id, data.books),
        )
        books_from_db = await self.repo.get_books_by_codes(
            self.mapper.map_book_payloads_to_codes(data.books),
        )
        conflicting_book = next(
            (book for book in books_from_db if book.author_id != author.id),
            None,
        )

        if conflicting_book is not None:
            raise AlreadyExistsException(
                message="A book with this code already exists",
                details=BookErrorDetails(book_code=conflicting_book.book_code),
            )

        for book in books_from_db:
            author.books.add(book)

        return self.mapper.map_author_to_read(author)

    async def get(self, author_id: int) -> Author:
        author = await self.repo.get(id=author_id)
        if author is None:
            raise ObjectNotFoundException(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
            )
        return self.mapper.map_author_to_read(author)

    async def get_paginated_list(self, limit: int, offset: int) -> AuthorsPaginatedList:
        authors, has_next = await self.repo.get_paginated_list(
            limit,
            offset,
        )
        return self.mapper.map_authors_paginated_list(
            authors,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete(self, author_id: int) -> None:
        author = await self.repo.get(id=author_id, for_update=True)
        if author is None:
            raise ObjectNotFoundException(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
            )
        await self.repo.get_books_by_codes(
            self.mapper.map_books_to_codes(list(author.books)),
        )
        for book in author.books:
            book.is_deleted = True
        await self.repo.delete(author)
        self.logger.info("author_deleted", author_id=author.id)

    async def update(self, author_id: int, data: AuthorUpdate) -> None:
        author = await self.repo.get(id=author_id, for_update=True)
        if author is None:
            raise ObjectNotFoundException(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
            )

        author_code = data.author_code
        books = data.books

        if author_code is not None and author_code != author.author_code:
            existing_author = await self.repo.get(
                author_code=author_code,
            )
            if existing_author is not None and existing_author.id != author_id:
                raise AlreadyExistsException(
                    message="An author with this code already exists",
                    details=AuthorErrorDetails(author_code=author_code),
                )

        self.mapper.apply_author_update_to_orm(data, author)

        if books is not None:
            await self.repo.create_books_do_nothing(
                self.mapper.map_book_updates_to_insert_values(author_id, books),
            )
            books_from_db = await self.repo.get_books_by_codes(
                self.mapper.map_book_payloads_to_codes(books),
            )
            conflicting_book = next(
                (book for book in books_from_db if book.author_id != author_id),
                None,
            )

            if conflicting_book is not None:
                raise AlreadyExistsException(
                    message="A book with this code already exists",
                    details=BookErrorDetails(
                        book_code=conflicting_book.book_code,
                    ),
                )
            books_from_db_by_code = {
                book.book_code: book for book in books_from_db
            }

            for book_data in books:
                book = books_from_db_by_code.get(book_data.book_code)
                book.title = book_data.title
                book.is_deleted = False

        await self.repo.update(author)
        self.logger.info("author_updated", author_id=author.id)
