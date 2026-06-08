from pydantic import BaseModel, ConfigDict, Field

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "number": "7799880044",
            "registrated_in": "Moscow"
        }
    ]
}


class PassportAddRequest(BaseModel):
    number: str = Field(min_length=1, max_length=10)
    registrated_in: str = Field(min_length=1, max_length=200)
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class PassportAdd(PassportAddRequest):
    person_id: int


class PassportRead(BaseModel):
    id: int
    number: str
    registrated_in: str


class Passport(PassportRead):
    model_config = ConfigDict(from_attributes=True)


class PassportPatch(BaseModel):
    number: str | None = None
    registrated_in: str | None = None
