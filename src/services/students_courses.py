from src.mappers.students_courses import (
    map_course_payload_to_orm,
    map_course_update_to_values,
    map_student_create_to_orm,
    map_student_update_courses,
    map_student_update_to_values,
    map_student_to_read,
    map_students_paginated_list,
)
from src.repositories.student import StudentRepository
from src.schemas.errors import StudentErrorDetails
from src.schemas.students import (
    Student,
    StudentCreate,
    StudentUpdate,
    StudentsPaginatedList,
)
from src.services.base import BaseService


class StudentsCoursesService(BaseService):
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    async def create(self, data: StudentCreate) -> Student:
        courses_data = data.courses

        existing_student = await self.repo.get(
            record_book_number=data.record_book_number
        )
        if existing_student is not None:
            self._raise_already_exists(
                message="A student with this record book number already exists",
                details=StudentErrorDetails(
                    record_book_number=data.record_book_number,
                ),
                record_book_number=data.record_book_number,
            )

        student = await self.repo.create(map_student_create_to_orm(data))
        for course_data in courses_data:
            reestr_number = course_data.reestr_number
            course = await self.repo.get_course_by_reestr_number(reestr_number)
            if course is None:
                course = await self.repo.create_course(
                    map_course_payload_to_orm(course_data)
                )
            elif course.title != course_data.title:
                await self.repo.update_course(
                    course,
                    map_course_update_to_values(course_data),
                )

            await self.repo.attach_course(student, course)

        self.logger.info("student_created", student_id=student.id)
        created_student = await self.repo.get(id=student.id)
        if created_student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student.id),
                student_id=student.id,
            )
        return map_student_to_read(created_student)

    async def get(self, student_id: int) -> Student:
        student = await self.repo.get(id=student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        return map_student_to_read(student)

    async def get_paginated_list(
        self, limit: int, offset: int
    ) -> StudentsPaginatedList:
        students, has_next = await self.repo.get_paginated_list(
            limit, offset
        )
        return map_students_paginated_list(
            students,
            has_next=has_next,
            limit=limit,
            offset=offset,
        )

    async def delete(self, student_id: int) -> None:
        student = await self.repo.get(id=student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        for course in list(student.courses):
            await self.repo.detach_course(student, course)
            if not await self.repo.course_has_active_students(course):
                await self.repo.delete_course(course)

        await self.repo.delete(student)
        self.logger.info("student_deleted", student_id=student.id)

    async def update(self, student_id: int, data: StudentUpdate) -> None:
        student = await self.repo.get(id=student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        courses_data = map_student_update_courses(data)
        student_data = map_student_update_to_values(data)

        # проверяем уникальность номера зачетной книжки при его изменении
        record_book_number = student_data.get("record_book_number")
        if record_book_number is not None:
            existing_student = await self.repo.get(
                record_book_number=record_book_number
            )
            if existing_student is not None and existing_student.id != student_id:
                self._raise_already_exists(
                    message="A student with this record book number already exists",
                    details=StudentErrorDetails(
                        record_book_number=record_book_number,
                    ),
                    record_book_number=record_book_number,
                )

        if student_data:
            await self.repo.update(student, student_data)
        if courses_data is not None:
            # синхронизируем курсы студента с payload
            existing_course_ids = {course.id for course in student.courses}
            target_course_ids: set[int] = set()
            for course_data in courses_data:
                reestr_number = course_data.reestr_number
                course = await self.repo.get_course_by_reestr_number(reestr_number)
                if course is None:
                    course = await self.repo.create_course(
                        map_course_payload_to_orm(course_data)
                    )
                elif course.title != course_data.title:
                    await self.repo.update_course(
                        course,
                        map_course_update_to_values(course_data),
                    )

                target_course_ids.add(course.id)
                await self.repo.attach_course(student, course)

            course_ids_to_detach = existing_course_ids - target_course_ids
            courses_to_detach = [
                course
                for course in student.courses
                if course.id in course_ids_to_detach
            ]
            for course in courses_to_detach:
                await self.repo.detach_course(student, course)
                # удаляем курс, если после отвязки он больше никому не назначен
                if not await self.repo.course_has_active_students(course):
                    await self.repo.delete_course(course)
        self.logger.info("student_updated", student_id=student.id)
