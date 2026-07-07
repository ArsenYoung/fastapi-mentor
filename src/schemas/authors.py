from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.books import Book, BookCreate

JSON_EXAMPLE = {
    "examples": [
        {
            "author_code": "000001",
            "first_name": "Leo",
            "last_name": "Tolstoy",
            "books": [
                {"book_code": "000001", "title": "War and Peace"},
                {"book_code": "000002", "title": "Sunday"},
            ],
        }
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "author_code": "000001",
            "first_name": "Leo",
            "last_name": "Tolstoy",
            "books": [
                {"book_code": "000001", "title": "War and Peace"},
                {"book_code": "000002", "title": "Sunday"},
            ],
        }
    ]
}


class AuthorCreate(BaseModel):
    author_code: str = Field(min_length=1, max_length=6)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    books: List[BookCreate]

    @field_validator("books")
    @classmethod
    def validate_books(cls, books: List[BookCreate]) -> List[BookCreate]:
        if not books:
            raise ValueError("At least one book is required")
        validate_unique_book_codes(books)
        return books

    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE,
    )


class Author(BaseModel):
    id: int
    author_code: str
    first_name: str
    last_name: str
    books: List[Book] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class AuthorBookUpdateRequest(BaseModel):
    book_code: str = Field(min_length=1, max_length=6)
    title: str = Field(min_length=1, max_length=100)


def validate_unique_book_codes(
    books: List[BookCreate] | List[AuthorBookUpdateRequest] | None,
) -> None:
    if books is None:
        return

    seen_codes = set()

    for book in books:
        if book.book_code in seen_codes:
            raise ValueError("Book codes must be unique")
        seen_codes.add(book.book_code)


class AuthorUpdate(BaseModel):
    author_code: str | None = Field(default=None, min_length=1, max_length=6)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    books: List[AuthorBookUpdateRequest] | None = None

    @field_validator("books")
    @classmethod
    def validate_books(
        cls,
        books: List[AuthorBookUpdateRequest] | None,
    ) -> List[AuthorBookUpdateRequest] | None:
        validate_unique_book_codes(books)
        return books

    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST,
    )


class AuthorsPaginatedList(BaseModel):
    items: List[Author]
    has_next: bool
    limit: int
    offset: int
