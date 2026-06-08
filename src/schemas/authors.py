from pydantic import BaseModel, ConfigDict, Field

from src.schemas.books import BookAddRequest, BookPatch, BookRead

JSON_EXAMPLE = {"examples": [
    {
        "author_code": "000001",
        "first_name": "Leo",
        "last_name": "Tolstoy",
        "books": [
            {"book_code": "000001", "title": "War and Peace"},
            {"book_code": "000002", "title": "Sunday"},
        ],
    }
]}

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


class AuthorAdd(BaseModel):
    author_code: str = Field(min_length=1, max_length=6)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class AuthorAddRequest(AuthorAdd):
    books: list[BookAddRequest] = Field(default_factory=list)
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE,
    )


class AuthorRead(BaseModel):
    id: int
    author_code: str
    first_name: str
    last_name: str
    books: list[BookRead] = Field(default_factory=list)


class Author(AuthorRead):
    model_config = ConfigDict(from_attributes=True)


class AuthorPatch(BaseModel):
    author_code: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    books: list[BookPatch] | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST,
    )

class AuthorsPage(BaseModel):
    items: list[AuthorRead]
    total: int
    limit: int
    offset: int
