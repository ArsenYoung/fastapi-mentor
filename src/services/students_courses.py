from src.mappers.students_courses import (
    map_course_to_payload,
    map_student_create_to_payload,
    map_student_to_read,
    map_student_update_to_payload,
    map_students_paginated_list,
)
from src.repositories.student import StudentRepository
from src.schemas.courses import CourseCreate
from src.schemas.students import (
    Student,
    StudentCreate,
    StudentCourseUpdateRequest,
    StudentUpdate,
    StudentsPaginatedList,
)
from src.services.base import BaseService


class StudentsCoursesService(BaseService):
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def _raise_if_duplicate_course_reestr_numbers(
        self,
        reestr_numbers: list[str],
        *,
        student_id: int | None = None,
    ) -> None:
        seen_numbers: set[str] = set()
        for reestr_number in reestr_numbers:
            if reestr_number in seen_numbers:
                self._raise_already_exists(
                    message="A course with this reestr number already exists",
                    student_id=student_id,
                    reestr_number=reestr_number,
                )
            seen_numbers.add(reestr_number)

    async def _raise_if_record_book_number_exists(
        self,
        record_book_number: str,
        *,
        exclude_student_id: int | None = None,
    ) -> None:
        student = await self.repo.get_student_by_record_book_number(record_book_number)
        if student is None or student.id == exclude_student_id:
            return
        self._raise_already_exists(
            message="A student with this record book number already exists",
            record_book_number=record_book_number,
        )

    async def _get_or_create_course(
        self,
        data: CourseCreate | StudentCourseUpdateRequest,
    ):
        return await self.repo.get_or_create_course(map_course_to_payload(data))

    async def create_student_with_courses(self, data: StudentCreate) -> None:
        self._raise_if_duplicate_course_reestr_numbers(
            [course.reestr_number for course in data.courses],
        )
        await self._raise_if_record_book_number_exists(data.record_book_number)
        student = await self.repo.create(**map_student_create_to_payload(data))
        for item in data.courses:
            course = await self._get_or_create_course(item)
            await self.repo.attach_course(student.id, course.id)
        self.logger.info("student_created", student_id=student.id)

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                student_id=student_id,
            )
        return map_student_to_read(student)
    
    async def get_students_with_courses_paginated_list(self, limit: int, offset: int) -> StudentsPaginatedList:
        students, has_next = await self.repo.get_students_with_courses_paginated_list(limit, offset)
        return map_students_paginated_list(
            students,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete_student_with_courses(self, student_id: int) -> None:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                student_id=student_id,
            )
        for course in student.courses:
            await self.repo.detach_course(student_id, course.id)
            await self.repo.delete_course_if_unused(course.id)
        await self.repo.delete(student_id)
        self.logger.info("student_deleted", student_id=student.id)

    async def update_student_with_courses(self, student_id: int, data: StudentUpdate) -> None:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                student_id=student_id,
            )
        if data.courses is not None:
            self._raise_if_duplicate_course_reestr_numbers(
                [course.reestr_number for course in data.courses],
                student_id=student_id,
            )
        if data.record_book_number is not None:
            await self._raise_if_record_book_number_exists(
                data.record_book_number,
                exclude_student_id=student_id,
            )
        student_data = map_student_update_to_payload(data)
        if student_data:
            await self.repo.update(student_id, student_data)
        if data.courses is not None:
            existing_course_ids = {course.id for course in student.courses}
            target_course_ids: set[int] = set()
            for item in data.courses:
                course = await self._get_or_create_course(item)
                target_course_ids.add(course.id)
                await self.repo.attach_course(student.id, course.id)

            course_ids_to_detach = existing_course_ids - target_course_ids
            for course_id in course_ids_to_detach:
                await self.repo.detach_course(student.id, course_id)
                await self.repo.delete_course_if_unused(course_id)
        self.logger.info("student_updated", student_id=student.id)
