from pydantic import BaseModel, ConfigDict, Field

from src.schemas.courses import Course, CourseCreate

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


class StudentCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    record_book_number: str = Field(min_length=1, max_length=8)
    courses: list[CourseCreate]
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class Student(BaseModel):
    id: int
    first_name: str
    last_name: str
    record_book_number: str
    courses: list[Course]
    model_config = ConfigDict(from_attributes=True)


class StudentCourseUpdateRequest(BaseModel):
    reestr_number: str = Field(min_length=1, max_length=4)
    title: str = Field(min_length=1, max_length=150)


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    record_book_number: str | None = None
    courses: list[StudentCourseUpdateRequest] | None = None
    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )

class StudentsPaginatedList(BaseModel):
    items: list[Student]
    has_next: bool
    limit: int
    offset: int
