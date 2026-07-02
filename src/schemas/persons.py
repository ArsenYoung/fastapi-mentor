from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.passports import Passport, PassportCreate, PassportUpdate

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "passport": {"number": "7788991010", "registrated_in": "Moscow"},
        }
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "passport": {"number": "7788991010", "registrated_in": "Moscow"},
        }
    ]
}


class PersonCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    passport: PassportCreate
    model_config = ConfigDict(json_schema_extra=JSON_EXAMPLE_ADD_REQUEST)


class Person(BaseModel):
    id: int
    first_name: str
    last_name: str
    passport: Passport
    model_config = ConfigDict(from_attributes=True)


class PersonUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    passport: PassportUpdate | None = None
    model_config = ConfigDict(json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST)


class PersonsPaginatedList(BaseModel):
    items: List[Person]
    has_next: bool
    limit: int
    offset: int
