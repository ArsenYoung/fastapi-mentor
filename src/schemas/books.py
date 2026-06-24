from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    book_code: str = Field(min_length=1, max_length=6)
    title: str = Field(min_length=1, max_length=100)


class Book(BaseModel):
    id: int
    book_code: str
    title: str
    model_config = ConfigDict(from_attributes=True)

class BookUpdate(BaseModel):
    book_code: str | None = None
    title: str | None = None
    is_deleted: bool | None = None
