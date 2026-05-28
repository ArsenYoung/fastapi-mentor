from pydantic import BaseModel, ConfigDict, Field

from src.schemas.passports import PassportAddRequest, PassportPatch, PassportRead


class PersonAdd(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class PersonAddRequest(PersonAdd):
    passport: PassportAddRequest
    model_config = ConfigDict(
          json_schema_extra={
              "examples": [
                  {
                    "first_name": "Алексей",
                    "last_name": "Попов",
                    "passport": {
                        "number": "7788991010",
                        "registrated_in": "Москва"
                    }
                  }
              ]
          }
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
          json_schema_extra={
              "examples": [
                  {
                    "first_name": "Алексей",
                    "last_name": "Попов",
                    "passport": {
                        "number": "7788991010",
                        "registrated_in": "Москва"
                    }
                  }
              ]
          }
      )
