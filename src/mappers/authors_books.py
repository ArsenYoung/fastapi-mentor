from typing import Any, Sequence

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import (
    Author,
    AuthorBookUpdateRequest,
    AuthorCreate,
    AuthorUpdate,
    AuthorsPaginatedList,
)
from src.schemas.books import Book, BookCreate


class AuthorsBooksMapper:
    def map_author_update_to_values(
        self,
        data: AuthorUpdate,
    ) -> dict[str, Any]:
        return data.model_dump(
            exclude={"books"},
            exclude_none=True,
            exclude_unset=True,
        )

    def map_book_update_to_orm(self, data: AuthorBookUpdateRequest) -> BooksOrm:
        return BooksOrm(**data.model_dump())

    def map_book_updates_to_orms(
        self,
        data: Sequence[AuthorBookUpdateRequest],
    ) -> list[BooksOrm]:
        return [self.map_book_update_to_orm(book) for book in data]

    def map_book_creates_to_orms(
        self,
        author_id: int,
        books: Sequence[BookCreate],
    ) -> list[BooksOrm]:
        return [
            BooksOrm(
                author_id=author_id,
                **book.model_dump(),
            )
            for book in books
        ]

    def map_book_payloads_to_codes(
        self,
        books: Sequence[BookCreate | AuthorBookUpdateRequest],
    ) -> list[str]:
        return [book.book_code for book in books]

    def map_books_to_codes(
        self,
        books: Sequence[BooksOrm],
    ) -> list[str]:
        return [book.book_code for book in books]

    def map_author_create_to_orm(self, data: AuthorCreate) -> AuthorsOrm:
        return AuthorsOrm(**data.model_dump(exclude={"books"}))

    def map_book_to_read(self, book: BooksOrm) -> Book:
        return Book.model_validate(book)

    def map_author_to_read(self, author: AuthorsOrm) -> Author:
        return Author(
            **Author.model_validate(
                author,
                from_attributes=True,
            ).model_dump(exclude={"books"}),
            books=[
                self.map_book_to_read(book)
                for book in sorted(
                    author.books,
                    key=lambda item: (item.id is None, item.id or 0, item.book_code),
                )
            ],
        )

    def map_authors_paginated_list(
        self,
        authors: Sequence[AuthorsOrm],
        *,
        has_next: bool,
        limit: int,
        offset: int,
    ) -> AuthorsPaginatedList:
        return AuthorsPaginatedList(
            items=[self.map_author_to_read(author) for author in authors],
            has_next=has_next,
            limit=limit,
            offset=offset,
        )
