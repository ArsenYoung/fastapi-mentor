from typing import Dict, List

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


def map_student_create_to_payload(data: StudentCreate) -> Dict[str, str]:
    return {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "record_book_number": data.record_book_number,
    }


def map_student_update_to_payload(data: StudentUpdate) -> Dict[str, str]:
    return data.model_dump(
        exclude_unset=True,
        exclude_none=True,
        exclude={"courses"},
    )


def map_course_to_payload(
    data: CourseCreate | StudentCourseUpdateRequest,
) -> Dict[str, str]:
    return {
        "reestr_number": data.reestr_number,
        "title": data.title,
    }


def map_courses_to_payloads(
    courses: List[CourseCreate] | List[StudentCourseUpdateRequest],
) -> List[Dict[str, str]]:
    return [
        map_course_to_payload(course)
        for course in courses
    ]


def map_course_payload_to_orm(payload: Dict[str, str]) -> CoursesOrm:
    return CoursesOrm(
        reestr_number=payload["reestr_number"],
        title=payload["title"],
    )


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
    students: List[StudentsOrm],
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
