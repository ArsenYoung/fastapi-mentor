from pydantic import BaseModel, ConfigDict, Field


class BookAddRequest(BaseModel):
    book_code: str = Field(min_length=1, max_length=6)
    title: str = Field(min_length=1, max_length=100)


class BookAdd(BookAddRequest):
    author_id: int


class BookRead(BaseModel):
    id: int
    book_code: str
    title: str

class Book(BookRead):
    model_config = ConfigDict(from_attributes=True)

class BookPatch(BaseModel):
    book_code: str
    title: str | None = None

class BookCreateRequest(BaseModel):
    book_code: str = Field(min_length=1, max_length=6)
    title: str = Field(min_length=1, max_length=100)
