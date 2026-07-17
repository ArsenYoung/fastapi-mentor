from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.mappers.students_courses import StudentCoursesMapper
from src.repositories.student import StudentRepository
from src.schemas.students import (
    Student,
    StudentCreate,
    StudentUpdate,
    StudentsPaginatedList,
)
from src.schemas.errors import StudentErrorDetails
from src.services.base import BaseService


class StudentsCoursesService(BaseService):
    def __init__(self, repo: StudentRepository, mapper: StudentCoursesMapper):
        self.repo = repo
        self.mapper = mapper

    async def create(self, data: StudentCreate) -> Student:
        student = await self.repo.create_do_nothing(
            self.mapper.map_student_create_to_orm(data),
        )
        if student is None:
            raise AlreadyExistsException(
                message="A student with this record book number already exists",
                details=StudentErrorDetails(
                    record_book_number=data.record_book_number,
                ),
            )

        await self.repo.create_courses_do_nothing(
            self.mapper.map_course_creates_to_orms(data.courses),
        )
        courses_from_db = await self.repo.get_courses_by_reestr_numbers(
            self.mapper.map_course_payloads_to_reestr_numbers(data.courses),
            for_update=True,
        )
        courses_from_db_by_reestr_number = {
            course.reestr_number: course for course in courses_from_db
        }
        for course_data in data.courses:
            course = courses_from_db_by_reestr_number.get(course_data.reestr_number)
            course.title = course_data.title
            student.courses.add(course)

        await self.repo.update(student)
        return self.mapper.map_student_to_read(student)

    async def get(self, student_id: int) -> Student:
        student = await self.repo.get(id=student_id)
        if student is None:
            raise ObjectNotFoundException(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
            )
        return self.mapper.map_student_to_read(student)

    async def get_paginated_list(
        self, limit: int, offset: int
    ) -> StudentsPaginatedList:
        students, has_next = await self.repo.get_paginated_list(limit, offset)
        return self.mapper.map_students_paginated_list(
            students,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete(self, student_id: int) -> None:
        student = await self.repo.get(id=student_id, for_update=True)
        if student is None:
            raise ObjectNotFoundException(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
            )
        detached_courses = set(student.courses)
        await self.repo.lock_courses_by_ids(
            self.mapper.map_courses_to_ids(list(detached_courses)),
        )
        student.courses.clear()
        await self.repo.delete(student)
        active_course_ids = await self.repo.get_course_ids_with_active_students(
            detached_courses,
        )
        orphan_courses = [
            course for course in detached_courses if course.id not in active_course_ids
        ]
        for course in orphan_courses:
            course.is_deleted = True
        self.logger.info("student_deleted", student_id=student.id)

    async def update(self, student_id: int, data: StudentUpdate) -> None:
        student = await self.repo.get(id=student_id, for_update=True)
        if student is None:
            raise ObjectNotFoundException(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
            )

        record_book_number = data.record_book_number
        courses = data.courses
        student_patch = self.mapper.map_student_update_to_orm(data)
        has_student_updates = (
            data.record_book_number is not None
            or data.first_name is not None
            or data.last_name is not None
        )

        if (
            record_book_number is not None
            and record_book_number != student.record_book_number
        ):
            existing_student = await self.repo.get(
                record_book_number=record_book_number,
            )
            if existing_student is not None and existing_student.id != student_id:
                raise AlreadyExistsException(
                    message="A student with this record book number already exists",
                    details=StudentErrorDetails(
                        record_book_number=record_book_number,
                    ),
                )

        if courses is not None:
            await self.repo.create_courses_do_nothing(
                self.mapper.map_course_updates_to_orms(courses),
            )
            courses_from_db = await self.repo.get_courses_by_reestr_numbers(
                self.mapper.map_course_payloads_to_reestr_numbers(courses),
                for_update=True,
            )
            courses_from_db_by_reestr_number = {
                course.reestr_number: course for course in courses_from_db
            }
            course_patches_by_reestr_number = {
                course.reestr_number: course
                for course in self.mapper.map_course_updates_to_orms(courses)
            }

            for course_data in courses:
                course = courses_from_db_by_reestr_number.get(
                    course_data.reestr_number
                )
                await self.repo.update_course_by_id(
                    course.id,
                    course_patches_by_reestr_number[course.reestr_number],
                )

            await self.repo.create_student_course_links_do_nothing(
                self.mapper.map_student_course_links_to_orms(
                    student_id,
                    courses_from_db,
                ),
            )

        if has_student_updates:
            await self.repo.update_by_id(student_id, student_patch)

        self.logger.info("student_updated", student_id=student.id)
