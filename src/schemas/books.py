from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

class BookRead(BaseModel):
    id: int
    title: str

class Book(BookRead):
    model_config = ConfigDict(from_attributes=True)