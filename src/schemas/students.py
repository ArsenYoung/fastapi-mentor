from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    courses: List[CourseCreate]

    @field_validator("courses")
    @classmethod
    def validate_courses(cls, courses: List[CourseCreate]) -> List[CourseCreate]:
        validate_unique_course_reestr_numbers(courses)
        return courses

    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_ADD_REQUEST
    )


class Student(BaseModel):
    id: int
    first_name: str
    last_name: str
    record_book_number: str
    courses: List[Course]
    model_config = ConfigDict(from_attributes=True)


class StudentCourseUpdateRequest(BaseModel):
    reestr_number: str = Field(min_length=1, max_length=4)
    title: str = Field(min_length=1, max_length=150)


def validate_unique_course_reestr_numbers(
    courses: List[CourseCreate] | List[StudentCourseUpdateRequest] | None,
) -> None:
    if courses is None:
        return

    seen_numbers = set()

    for course in courses:
        if course.reestr_number in seen_numbers:
            raise ValueError("Course reestr numbers must be unique")
        seen_numbers.add(course.reestr_number)


class StudentUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    record_book_number: str | None = Field(default=None, min_length=1, max_length=8)
    courses: List[StudentCourseUpdateRequest] | None = None

    @field_validator("courses")
    @classmethod
    def validate_courses(
        cls,
        courses: List[StudentCourseUpdateRequest] | None,
    ) -> List[StudentCourseUpdateRequest] | None:
        validate_unique_course_reestr_numbers(courses)
        return courses

    model_config = ConfigDict(
        json_schema_extra=JSON_EXAMPLE_PATCH_REQUEST
    )

class StudentsPaginatedList(BaseModel):
    items: List[Student]
    has_next: bool
    limit: int
    offset: int
