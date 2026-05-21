from pydantic import BaseModel, ConfigDict, Field

from src.schemas.books import BookCreate, BookRead


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    books: list[BookCreate] = Field(default_factory=list)

class AuthorRead(BaseModel):
    id: int
    name: str
    books: list[BookRead] = Field(default_factory=list)

class Author(AuthorRead):
    model_config = ConfigDict(from_attributes=True)