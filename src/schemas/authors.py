from pydantic import BaseModel, ConfigDict, Field

from src.schemas.books import BookAddRequest, BookPatch, BookRead

JSON_EXAMPLE = {"examples": [
    {
        "first_name": "Лев",
        "last_name": "Толстой",
        "books": [
            {"title": "Война и Мир"},
            {"title": "Воскресенье"},
        ],
    }
]}


class AuthorAdd(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class AuthorAddRequest(AuthorAdd):
    books: list[BookAddRequest] = Field(default_factory=list)
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE,
    )


class AuthorRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    books: list[BookRead] = Field(default_factory=list)


class Author(AuthorRead):
    model_config = ConfigDict(from_attributes=True)


class AuthorPatch(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    books: list[BookPatch] | None = None

class AuthorsPage(BaseModel):
    items: list[AuthorRead]
    total: int
    limit: int
    offset: int