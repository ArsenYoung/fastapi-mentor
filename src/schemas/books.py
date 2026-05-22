from pydantic import BaseModel, ConfigDict, Field


class BookAddRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class BookAdd(BookAddRequest):
    author_id: int


class BookRead(BaseModel):
    id: int
    author_id: int
    title: str

class Book(BookRead):
    model_config = ConfigDict(from_attributes=True)
