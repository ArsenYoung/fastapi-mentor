from pydantic import BaseModel, ConfigDict, Field

from src.schemas.courses import CourseAddRequest, CourseRead

JSON_EXAMPLE_ADD_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "record_book_number": "212866",
            "courses": [
                {
                    "reestr_number": "2MMI",
                    "title": "Mechanical Engineering",
                },
                {
                    "reestr_number": "ICBN",
                    "title": "Computer Science",
                },
            ]
        }
    ]
}

JSON_EXAMPLE_PATCH_REQUEST = {
    "examples": [
        {
            "first_name": "Alexey",
            "last_name": "Popov",
            "record_book_number": "212866",
            "courses": [
                {
                    "reestr_number": "2MMI",
                    "title": "Mechanical Engineering",
                },
                {
                    "reestr_number": "ICBN",
                    "title": "Computer Science",
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


class StudentCourseUpsertRequest(BaseModel):
    reestr_number: str = Field(min_length=1, max_length=4)
    title: str = Field(min_length=1, max_length=150)


class StudentPatch(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    record_book_number: str | None = None
    courses: list[StudentCourseUpsertRequest] | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )

class StudentsPage(BaseModel):
    items: list[StudentRead]
    total: int
    limit: int
    offset: int

class StudentCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    record_book_number: str = Field(min_length=1, max_length=8)
