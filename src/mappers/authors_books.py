from typing import Mapping, Sequence

from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import Author, AuthorsPaginatedList
from src.schemas.books import Book


def map_book_payload_to_orm(author_id: int, payload: Mapping[str, str]) -> BooksOrm:
    return BooksOrm(
        author_id=author_id,
        book_code=payload["book_code"],
        title=payload["title"],
    )


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
