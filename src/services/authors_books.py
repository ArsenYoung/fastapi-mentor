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

        author = await self.repo.create_author(
            self.mapper.map_author_create_to_orm(data),
        )
        if author is None:
            raise AlreadyExistsException(
                message="An author with this code already exists",
                details=AuthorErrorDetails(author_code=data.author_code),
            )

        book_orms = self.mapper.map_book_creates_to_orms(
            author.id,
            data.books,
        )
        created_books = await self.repo.create_books(book_orms)

        if len(created_books) != len(book_orms):
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
        author = await self.repo.get(id=author_id)
        if author is None:
            raise ObjectNotFoundException(
                message="Author not found",
                details=AuthorErrorDetails(author_id=author_id),
            )

        books = data.books
        author_patch = self.mapper.map_author_update_to_orm(data)

        updated_author = await self.repo.update_author_by_id(author_id, author_patch)
        if updated_author is None:
            raise AlreadyExistsException(
                message="An author with this code already exists",
                details=AuthorErrorDetails(author_code=data.author_code),
            )

        if books is not None:
            book_patches = self.mapper.map_book_updates_to_orms(books)
            requested_book_codes = self.mapper.map_book_payloads_to_codes(books)
            updated_book_codes = set(
                await self.repo.update_books_by_author_id(
                    author_id,
                    book_patches,
                )
            )

            if len(requested_book_codes) != len(updated_book_codes):
                unresolved_book_codes = list(
                    set(requested_book_codes) - updated_book_codes,
                )
                existing_books = await self.repo.get_books_by_codes(
                    unresolved_book_codes,
                )
                existing_book_codes = set(
                    self.mapper.map_books_to_codes(existing_books),
                )

                for book_code in unresolved_book_codes:
                    if book_code not in existing_book_codes:
                        raise ObjectNotFoundException(
                            message="Book not found",
                            details=BookErrorDetails(book_code=book_code),
                        )

                    raise AlreadyExistsException(
                        message="A book with this code already exists",
                        details=BookErrorDetails(book_code=book_code),
                    )

        self.logger.info("author_updated", author_id=author.id)
