from src.models.students import StudentsOrm
from src.schemas.courses import Course
from src.schemas.students import Student, StudentsPaginatedList


def map_course_to_read(course) -> Course:
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
    students: list[StudentsOrm],
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
