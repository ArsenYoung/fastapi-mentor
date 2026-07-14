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
        book_codes = self.mapper.map_book_payloads_to_codes(data.books)
        author_values = self.mapper.map_author_create_to_insert_values(data)

        author = await self.repo.create_do_nothing(author_values)
        if author is None:
            raise AlreadyExistsException(
                message="An author with this code already exists",
                details=AuthorErrorDetails(author_code=data.author_code),
            )

        book_values = self.mapper.map_book_creates_to_insert_values(
            author.id,
            data.books,
        )
        created_books = await self.repo.create_books_do_nothing(book_values)

        if len(created_books) != len(book_values):
            created_book_codes = set(self.mapper.map_books_to_codes(created_books))
            for book_code in book_codes:
                if book_code not in created_book_codes:
                    raise AlreadyExistsException(
                        message="A book with this code already exists",
                        details=BookErrorDetails(book_code=book_code),
                    )

        author.books.update(created_books)
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
        books = await self.repo.get_books_by_author_id(
            author_id,
            for_update=True,
        )
        for book in books:
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
            book_codes = self.mapper.map_book_payloads_to_codes(books)
            books_with_requested_codes = await self.repo.get_books_by_codes(
                book_codes,
                for_update=True,
            )
            found_book_codes = {
                book.book_code for book in books_with_requested_codes
            }

            for book_code in book_codes:
                if book_code not in found_book_codes:
                    raise ObjectNotFoundException(
                        message="Book not found",
                        details=BookErrorDetails(book_code=book_code),
                    )

            for book in books_with_requested_codes:
                if book.author_id != author_id:
                    raise AlreadyExistsException(
                        message="A book with this code already exists",
                        details=BookErrorDetails(
                            book_code=book.book_code,
                        ),
                    )
            self.mapper.apply_book_updates_to_orms(
                books,
                books_with_requested_codes,
            )

        await self.repo.update(author)
        self.logger.info("author_updated", author_id=author.id)
