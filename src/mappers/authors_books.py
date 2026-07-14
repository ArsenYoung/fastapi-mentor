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
    def apply_author_update_to_orm(
        self,
        data: AuthorUpdate,
        author: AuthorsOrm,
    ) -> AuthorsOrm:
        if data.author_code is not None:
            author.author_code = data.author_code
        if data.first_name is not None:
            author.first_name = data.first_name
        if data.last_name is not None:
            author.last_name = data.last_name
        return author

    def map_book_update_to_orm(self, data: AuthorBookUpdateRequest) -> BooksOrm:
        return BooksOrm(
            book_code=data.book_code,
            title=data.title,
        )

    def map_author_create_to_insert_values(
        self,
        data: AuthorCreate,
    ) -> dict[str, Any]:
        return {
            "author_code": data.author_code,
            "first_name": data.first_name,
            "last_name": data.last_name,
        }

    def map_book_updates_to_insert_values(
        self,
        author_id: int,
        books: Sequence[AuthorBookUpdateRequest],
    ) -> list[dict[str, Any]]:
        return [
            {
                "author_id": author_id,
                "book_code": book.book_code,
                "title": book.title,
            }
            for book in books
        ]

    def map_book_creates_to_insert_values(
        self,
        author_id: int,
        books: Sequence[BookCreate],
    ) -> list[dict[str, Any]]:
        return [
            {
                "author_id": author_id,
                "book_code": book.book_code,
                "title": book.title,
            }
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
        return AuthorsOrm(
            author_code=data.author_code,
            first_name=data.first_name,
            last_name=data.last_name,
        )

    def map_book_to_read(self, book: BooksOrm) -> Book:
        return Book(
            id=book.id,
            book_code=book.book_code,
            title=book.title,
        )

    def map_author_to_read(self, author: AuthorsOrm) -> Author:
        return Author(
            id=author.id,
            author_code=author.author_code,
            first_name=author.first_name,
            last_name=author.last_name,
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
