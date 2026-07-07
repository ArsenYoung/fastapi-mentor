from typing import Sequence

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import (
    Author,
    AuthorBookUpdateRequest,
    AuthorCreate,
    AuthorsPaginatedList,
)
from src.schemas.books import Book


class AuthorsBooksMapper:
    def map_book_update_to_orm(self, data: AuthorBookUpdateRequest) -> BooksOrm:
        return BooksOrm(
            book_code=data.book_code,
            title=data.title,
        )

    def map_author_create_to_orm(self, data: AuthorCreate) -> AuthorsOrm:
        author = AuthorsOrm(
            author_code=data.author_code,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        for book in data.books:
            author.books.add(
                BooksOrm(
                    book_code=book.book_code,
                    title=book.title,
                )
            )
        return author

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
