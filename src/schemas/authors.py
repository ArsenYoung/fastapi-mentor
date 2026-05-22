from pydantic import BaseModel, ConfigDict, Field

from src.schemas.books import BookAddRequest, BookRead

class AuthorAdd(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class AuthorAddRequest(AuthorAdd):
    books: list[BookAddRequest] = Field(default_factory=list)

class AuthorRead(BaseModel):
    id: int
    name: str
    books: list[BookRead] = Field(default_factory=list)

class Author(AuthorRead):
    model_config = ConfigDict(from_attributes=True)