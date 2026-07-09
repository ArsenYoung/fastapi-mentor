from typing import Any, Sequence

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.schemas.courses import Course, CourseCreate
from src.schemas.students import (
    Student,
    StudentCourseUpdateRequest,
    StudentCreate,
    StudentUpdate,
    StudentsPaginatedList,
)


class StudentCoursesMapper:
    def map_student_create_to_orm(self, data: StudentCreate) -> StudentsOrm:
        return StudentsOrm(
            first_name=data.first_name,
            last_name=data.last_name,
            record_book_number=data.record_book_number,
        )

    def map_student_update_to_fields(
        self,
        data: StudentUpdate,
    ) -> dict[str, Any]:
        return data.model_dump(
            exclude={"courses"},
        )

    def map_course_payload_to_orm(
        self,
        data: CourseCreate | StudentCourseUpdateRequest,
    ) -> CoursesOrm:
        return CoursesOrm(
            reestr_number=data.reestr_number,
            title=data.title,
        )

    def map_course_updates_to_insert_values(
        self,
        courses: Sequence[StudentCourseUpdateRequest],
    ) -> list[tuple[str, str]]:
        return [(course.reestr_number, course.title) for course in courses]

    def map_course_payloads_to_reestr_numbers(
        self,
        courses: Sequence[CourseCreate | StudentCourseUpdateRequest],
    ) -> list[str]:
        return [course.reestr_number for course in courses]

    def map_courses_to_reestr_numbers(
        self,
        courses: Sequence[CoursesOrm],
    ) -> list[str]:
        return [course.reestr_number for course in courses]

    def map_courses_to_ids(
        self,
        courses: Sequence[CoursesOrm],
    ) -> list[int]:
        return [course.id for course in courses if course.id is not None]

    def map_course_to_read(self, course: CoursesOrm) -> Course:
        return Course(
            id=course.id,
            reestr_number=course.reestr_number,
            title=course.title,
        )

    def map_student_to_read(self, student: StudentsOrm) -> Student:
        return Student(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            record_book_number=student.record_book_number,
            courses=[
                self.map_course_to_read(course)
                for course in sorted(
                    student.courses,
                    key=lambda item: (
                        item.id is None,
                        item.id or 0,
                        item.reestr_number,
                    ),
                )
            ],
        )

    def map_students_paginated_list(
        self,
        students: Sequence[StudentsOrm],
        *,
        has_next: bool,
        limit: int,
        offset: int,
    ) -> StudentsPaginatedList:
        return StudentsPaginatedList(
            items=[self.map_student_to_read(student) for student in students],
            has_next=has_next,
            limit=limit,
            offset=offset,
        )
