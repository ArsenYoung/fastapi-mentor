from pydantic import BaseModel, ConfigDict, Field

from src.schemas.passports import PassportAddRequest, PassportPatch, PassportRead

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "passport": {
                "number": "7788991010",
                "registrated_in": "Moscow"
            }
        }
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "passport": {
                "number": "7788991010",
                "registrated_in": "Moscow"
            }
        }
    ]
}


class PersonAdd(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class PersonAddRequest(PersonAdd):
    passport: PassportAddRequest
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class PersonRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    passport: PassportRead


class Person(PersonRead):
    model_config = ConfigDict(from_attributes=True)


class PersonPatch(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    passport: PassportPatch | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )

class PersonPage(BaseModel):
    items: list[PersonRead]
    total: int
    limit: int
    offset: int
