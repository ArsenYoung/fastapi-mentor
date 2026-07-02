from typing import Sequence

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import (
    Author,
    AuthorBookUpdateRequest,
    AuthorCreate,
    AuthorsPaginatedList,
    AuthorUpdate,
)
from src.schemas.books import Book


def map_book_update_to_orm(
    author_id: int,
    data: AuthorBookUpdateRequest,
) -> BooksOrm:
    return BooksOrm(
        author_id=author_id,
        book_code=data.book_code,
        title=data.title,
    )


def map_author_create_to_orm(data: AuthorCreate) -> AuthorsOrm:
    author = AuthorsOrm(
        author_code=data.author_code,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    author.books.extend(
        BooksOrm(
            book_code=book.book_code,
            title=book.title,
        )
        for book in data.books
    )
    return author


def map_author_update_to_values(data: AuthorUpdate) -> dict[str, object]:
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude={"books"},
    )


def map_author_update_books(
    data: AuthorUpdate,
) -> list[AuthorBookUpdateRequest] | None:
    if "books" not in data.model_fields_set or data.books is None:
        return None
    return data.books


def map_book_update_to_values(data: AuthorBookUpdateRequest) -> dict[str, object]:
    return {
        "title": data.title,
        "is_deleted": False,
    }


def map_book_to_read(book: BooksOrm) -> Book:
    return Book(
        id=book.id,
        book_code=book.book_code,
        title=book.title,
    )


def map_author_to_read(author: AuthorsOrm) -> Author:
    return Author(
        id=author.id,
        author_code=author.author_code,
        first_name=author.first_name,
        last_name=author.last_name,
        books=[map_book_to_read(book) for book in author.books],
    )


def map_authors_paginated_list(
    authors: Sequence[AuthorsOrm],
    *,
    has_next: bool,
    limit: int,
    offset: int,
) -> AuthorsPaginatedList:
    return AuthorsPaginatedList(
        items=[
            map_author_to_read(author)
            for author in authors
        ],
        has_next=has_next,
        limit=limit,
        offset=offset,
    )
