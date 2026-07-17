from typing import Sequence

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
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
        return StudentsOrm(**data.model_dump(exclude={"courses"}))

    def map_student_update_to_orm(
        self,
        data: StudentUpdate,
    ) -> StudentsOrm:
        return StudentsOrm(
            **data.model_dump(
                exclude={"courses"},
                exclude_none=True,
                exclude_unset=True,
            )
        )

    def map_course_payload_to_orm(
        self,
        data: CourseCreate | StudentCourseUpdateRequest,
    ) -> CoursesOrm:
        return CoursesOrm(**data.model_dump())

    def map_course_creates_to_orms(
        self,
        courses: Sequence[CourseCreate],
    ) -> list[CoursesOrm]:
        return [self.map_course_payload_to_orm(course) for course in courses]

    def map_course_updates_to_orms(
        self,
        courses: Sequence[StudentCourseUpdateRequest],
    ) -> list[CoursesOrm]:
        return [self.map_course_payload_to_orm(course) for course in courses]

    def map_course_payloads_to_reestr_numbers(
        self,
        courses: Sequence[CourseCreate | StudentCourseUpdateRequest],
    ) -> list[str]:
        return [course.reestr_number for course in courses]

    def map_courses_to_ids(
        self,
        courses: Sequence[CoursesOrm],
    ) -> list[int]:
        return [course.id for course in courses if course.id is not None]

    def map_student_course_links_to_orms(
        self,
        student_id: int,
        courses: Sequence[CoursesOrm],
    ) -> list[StudentsCoursesOrm]:
        return [
            StudentsCoursesOrm(
                student_id=student_id,
                course_id=course.id,
            )
            for course in courses
            if course.id is not None
        ]

    def map_course_to_read(self, course: CoursesOrm) -> Course:
        return Course.model_validate(course)

    def map_student_to_read(self, student: StudentsOrm) -> Student:
        return Student(
            **Student.model_validate(
                student,
                from_attributes=True,
            ).model_dump(exclude={"courses"}),
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
