from typing import Sequence

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.schemas.courses import Course, CourseCreate
from src.schemas.students import (
    Student,
    StudentCourseUpdateRequest,
    StudentCreate,
    StudentsPaginatedList,
    StudentUpdate,
)


def map_student_create_to_orm(data: StudentCreate) -> StudentsOrm:
    return StudentsOrm(
        first_name=data.first_name,
        last_name=data.last_name,
        record_book_number=data.record_book_number,
    )


def map_student_update_to_values(data: StudentUpdate) -> dict[str, object]:
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude={"courses"},
    )


def map_student_update_courses(
    data: StudentUpdate,
) -> list[StudentCourseUpdateRequest] | None:
    if "courses" not in data.model_fields_set or data.courses is None:
        return None
    return data.courses


def map_course_payload_to_orm(
    data: CourseCreate | StudentCourseUpdateRequest,
) -> CoursesOrm:
    return CoursesOrm(
        reestr_number=data.reestr_number,
        title=data.title,
    )


def map_course_update_to_values(
    data: CourseCreate | StudentCourseUpdateRequest,
) -> dict[str, object]:
    return {"title": data.title}


def map_course_to_read(course: CoursesOrm) -> Course:
    return Course(
        id=course.id,
        reestr_number=course.reestr_number,
        title=course.title,
    )


def map_student_to_read(student: StudentsOrm) -> Student:
    return Student(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        record_book_number=student.record_book_number,
        courses=[map_course_to_read(course) for course in student.courses],
    )


def map_students_paginated_list(
    students: Sequence[StudentsOrm],
    *,
    has_next: bool,
    limit: int,
    offset: int,
) -> StudentsPaginatedList:
    return StudentsPaginatedList(
        items=[
            map_student_to_read(student)
            for student in students
        ],
        has_next=has_next,
        limit=limit,
        offset=offset,
    )
