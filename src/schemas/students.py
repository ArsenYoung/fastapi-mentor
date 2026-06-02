from pydantic import BaseModel, ConfigDict, Field

from src.schemas.courses import CourseAddRequest, CoursePatch, CourseRead

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "first_name": "Алексей",
            "last_name": "Попов",
            "record_book_number": "212866",
            "courses": [
                {
                    "reestr_number": "2MMI",
                    "title": "Машиностроение",
                },
                {
                    "reestr_number": "ICBN",
                    "title": "Информатика",
                },
            ]
        }
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "first_name": "Алексей",
            "last_name": "Попов",
            "record_book_number": "212866",
            "courses": [
                {
                    "reestr_number": "2MMI",
                    "title": "Машиностроение",
                },
                {
                    "reestr_number": "ICBN",
                    "title": "Информатика",
                },
            ]
        }
    ]
}


class StudentAddRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    record_book_number: str = Field(min_length=1, max_length=8)
    courses: list[CourseAddRequest]
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class StudentRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    record_book_number: str
    courses: list[CourseRead]


class Student(StudentRead):
    model_config = ConfigDict(from_attributes=True)


class StudentPatch(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    record_book_number: str | None = None
    courses: list[CoursePatch] | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )
