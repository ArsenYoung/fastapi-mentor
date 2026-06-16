from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import Author, AuthorBookUpdateRequest, AuthorCreate, AuthorsPaginatedList, AuthorUpdate
from src.schemas.books import Book, BookCreate


def map_author_create_to_payload(data: AuthorCreate) -> dict[str, str]:
    return {
        "author_code": data.author_code,
        "first_name": data.first_name,
        "last_name": data.last_name,
    }


def map_author_update_to_payload(data: AuthorUpdate) -> dict[str, str]:
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude={"books"},
    )


def map_books_to_payloads(
    books: list[BookCreate] | list[AuthorBookUpdateRequest],
) -> list[dict[str, str]]:
    return [
        {
            "book_code": book.book_code,
            "title": book.title,
        }
        for book in books
    ]


def map_book_payload_to_orm(author_id: int, payload: dict[str, str]) -> BooksOrm:
    return BooksOrm(
        author_id=author_id,
        book_code=payload["book_code"],
        title=payload["title"],
    )


def map_author_with_books_to_updated_state(
    author: AuthorsOrm,
    author_payload: dict[str, str],
    books_payloads: list[dict[str, str]] | None,
) -> AuthorsOrm:
    for field, value in author_payload.items():
        setattr(author, field, value)

    if books_payloads is None:
        return author

    existing_books_by_code = {
        book.book_code: book
        for book in author.books
    }
    target_codes = {book_payload["book_code"] for book_payload in books_payloads}
    for book in author.books:
        if book.book_code not in target_codes:
            book.is_deleted = True

    for book_payload in books_payloads:
        existing_book = existing_books_by_code.get(book_payload["book_code"])
        if existing_book is None:
            author.books.append(map_book_payload_to_orm(author.id, book_payload))
            continue
        _map_book_to_updated_state(existing_book, book_payload)
    return author


def _map_book_to_updated_state(
    existing_book: BooksOrm,
    payload: dict[str, str],
) -> None:
    existing_book.title = payload["title"]
    existing_book.is_deleted = False


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
    authors: list[AuthorsOrm],
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
