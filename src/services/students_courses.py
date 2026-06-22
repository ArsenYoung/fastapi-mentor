from typing import Mapping, Sequence, Set

from sqlalchemy import exists, func, select, update

from src.mappers.students_courses import (
    map_course_payload_to_orm,
    map_student_to_read,
    map_students_paginated_list,
)
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.student import StudentRepository
from src.schemas.students import (
    Student,
    StudentCreate,
    StudentUpdate,
    StudentsPaginatedList,
)
from src.schemas.errors import CourseErrorDetails, StudentErrorDetails
from src.services.base import BaseService


class StudentsCoursesService(BaseService):
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def _raise_if_duplicate_course_reestr_numbers(
        self,
        reestr_numbers: Sequence[str],
        *,
        student_id: int | None = None,
    ) -> None:
        seen_numbers: Set[str] = set()
        for reestr_number in reestr_numbers:
            if reestr_number in seen_numbers:
                self._raise_already_exists(
                    message="A course with this reestr number already exists",
                    details=CourseErrorDetails(
                        reestr_number=reestr_number,
                    ),
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
            details=StudentErrorDetails(
                record_book_number=record_book_number,
            ),
            record_book_number=record_book_number,
        )

    async def _get_or_create_course(self, course_data: Mapping[str, str]) -> CoursesOrm:
        reestr_number = course_data["reestr_number"]
        title = course_data["title"]

        await self._acquire_advisory_lock(f"course:{reestr_number}")
        course = await self._get_course_by_reestr_number(reestr_number)
        if course is None:
            return await self._create_course(course_data)
        if course.title != title:
            course.title = title
            await self.repo.flush()
        return course

    async def _get_course_by_reestr_number(
        self, reestr_number: str
    ) -> CoursesOrm | None:
        stmt = select(CoursesOrm).where(
            CoursesOrm.is_deleted.is_(False),
            CoursesOrm.reestr_number == reestr_number,
        )
        result = await self.repo.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _acquire_advisory_lock(self, lock_key: str) -> None:
        await self.repo.session.execute(
            select(func.pg_advisory_xact_lock(func.hashtext(lock_key)))
        )

    async def _create_course(self, course_data: Mapping[str, str]) -> CoursesOrm:
        course = map_course_payload_to_orm(course_data)
        self.repo.session.add(course)
        await self.repo.flush()
        return course

    def _get_course_link(
        self,
        student: StudentsOrm,
        course_id: int,
    ) -> StudentsCoursesOrm | None:
        return next(
            (
                link
                for link in student.course_link
                if link.course_id == course_id
            ),
            None,
        )

    async def _attach_course(self, student: StudentsOrm, course: CoursesOrm) -> None:
        link = self._get_course_link(student, course.id)
        if link is not None and not link.is_deleted:
            return
        await self._acquire_advisory_lock(f"course-links:{course.id}")
        if link is not None:
            link.is_deleted = False
            link.courses = course
        else:
            student.course_link.append(
                StudentsCoursesOrm(
                    course_id=course.id,
                    courses=course,
                )
            )
        await self.repo.flush()

    async def _create_course_link(self, student_id: int, course_id: int) -> None:
        await self._acquire_advisory_lock(f"course-links:{course_id}")
        self.repo.session.add(
            StudentsCoursesOrm(
                student_id=student_id,
                course_id=course_id,
            )
        )
        await self.repo.flush()

    async def _detach_course(self, student: StudentsOrm, course: CoursesOrm) -> None:
        link = self._get_course_link(student, course.id)
        if link is None or link.is_deleted:
            return
        await self._acquire_advisory_lock(f"course-links:{course.id}")
        link.is_deleted = True
        await self.repo.flush()

    async def _delete_course_if_unused(self, course_id: int) -> None:
        await self._acquire_advisory_lock(f"course-links:{course_id}")
        await self.repo.session.execute(
            update(CoursesOrm)
            .where(
                CoursesOrm.id == course_id,
                CoursesOrm.is_deleted.is_(False),
                ~exists().where(
                    StudentsCoursesOrm.course_id == CoursesOrm.id,
                    StudentsCoursesOrm.is_deleted.is_(False),
                ),
            )
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )

    async def create_student_with_courses(self, data: StudentCreate) -> Student:
        courses_data = [course.model_dump() for course in data.courses]
        self._raise_if_duplicate_course_reestr_numbers(
            [course["reestr_number"] for course in courses_data],
        )
        await self._raise_if_record_book_number_exists(data.record_book_number)
        student = await self.repo.create(**data.model_dump(exclude={"courses"}))
        for course_data in courses_data:
            course = await self._get_or_create_course(course_data)
            await self._create_course_link(student.id, course.id)
        self.logger.info("student_created", student_id=student.id)
        created_student = await self.repo.get_student_with_courses(student.id)
        if created_student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student.id),
                student_id=student.id,
            )
        return map_student_to_read(created_student)

    async def get_student_with_courses(self, student_id: int) -> Student:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        return map_student_to_read(student)

    async def get_students_with_courses_paginated_list(
        self, limit: int, offset: int
    ) -> StudentsPaginatedList:
        students, has_next = await self.repo.get_students_with_courses_paginated_list(
            limit, offset
        )
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
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        for course in list(student.courses):
            await self._detach_course(student, course)
            await self._delete_course_if_unused(course.id)
        await self.repo.delete(student_id)
        self.logger.info("student_deleted", student_id=student.id)

    async def update_student_with_courses(
        self, student_id: int, data: StudentUpdate
    ) -> None:
        student = await self.repo.get_student_with_courses(student_id)
        if student is None:
            self._raise_not_found(
                message="Student not found",
                details=StudentErrorDetails(student_id=student_id),
                student_id=student_id,
            )
        courses_data = (
            [course.model_dump() for course in data.courses]
            if data.courses is not None
            else None
        )
        if courses_data is not None:
            self._raise_if_duplicate_course_reestr_numbers(
                [course["reestr_number"] for course in courses_data],
                student_id=student_id,
            )
        if data.record_book_number is not None:
            await self._raise_if_record_book_number_exists(
                data.record_book_number,
                exclude_student_id=student_id,
            )
        student_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"courses"},
        )
        if student_data:
            await self.repo.update(student_id, student_data)
        if courses_data is not None:
            existing_course_ids = {course.id for course in student.courses}
            target_course_ids: Set[int] = set()
            for course_data in courses_data:
                course = await self._get_or_create_course(course_data)
                target_course_ids.add(course.id)
                await self._attach_course(student, course)

            course_ids_to_detach = existing_course_ids - target_course_ids
            courses_to_detach = [
                course
                for course in student.courses
                if course.id in course_ids_to_detach
            ]
            for course in courses_to_detach:
                await self._detach_course(student, course)
                await self._delete_course_if_unused(course.id)
        self.logger.info("student_updated", student_id=student.id)
