from sqlalchemy import delete, exists, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload, selectinload

from src.mappers.students_courses import map_course_payload_to_orm
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository):
    model = StudentsOrm

    def _get_with_courses_stmt(self):
        return (
            select(StudentsOrm)
            .where(StudentsOrm.is_deleted.is_(False))
            .options(
                selectinload(
                    StudentsOrm.course_link.and_(StudentsCoursesOrm.is_deleted.is_(False))
                ).joinedload(
                    StudentsCoursesOrm.courses.and_(CoursesOrm.is_deleted.is_(False))
                )
            )
            .order_by(StudentsOrm.id)
        )

    async def _get_student_with_courses(self, student_id: int) -> StudentsOrm | None:
        stmt = self._get_with_courses_stmt().where(StudentsOrm.id == student_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    async def get_student_by_record_book_number(self, record_book_number: str) -> StudentsOrm | None:
        stmt = (
            select(StudentsOrm)
            .where(
                StudentsOrm.is_deleted.is_(False),
                StudentsOrm.record_book_number == record_book_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_student_with_courses(self, student_id: int) -> StudentsOrm | None:
        return await self._get_student_with_courses(student_id)

    async def get_students_with_courses_paginated_list(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[StudentsOrm], bool]:
        stmt = self._get_with_courses_stmt().offset(offset).limit(limit + 1)
        result = await self.session.execute(stmt)
        students = list(result.unique().scalars().all())
        has_next = len(students) > limit
        return students[:limit], has_next
    
    async def create(
        self,
        first_name: str,
        last_name: str,
        record_book_number: str,
    ) -> StudentsOrm:
        return await super().create(
            first_name=first_name,
            last_name=last_name,
            record_book_number=record_book_number,
        )

    async def get_course_by_reestr_number(self, reestr_number: str) -> CoursesOrm | None:
        stmt = (
            select(CoursesOrm)
            .where(
                CoursesOrm.is_deleted.is_(False),
                CoursesOrm.reestr_number == reestr_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _acquire_advisory_lock(self, lock_key: str) -> None:
        await self.session.execute(
            select(func.pg_advisory_xact_lock(func.hashtext(lock_key)))
        )

    async def create_course(self, course_data: dict[str, str]) -> CoursesOrm:
        course = map_course_payload_to_orm(course_data)
        self.session.add(course)
        await self.session.flush()
        return course

    async def get_or_create_course(self, course_data: dict[str, str]) -> CoursesOrm:
        reestr_number = course_data["reestr_number"]
        title = course_data["title"]
        await self._acquire_advisory_lock(f"course:{reestr_number}")
        course = await self.get_course_by_reestr_number(reestr_number)
        if course is None:
            return await self.create_course(course_data)
        if course.title != title:
            await self.update_course(course.id, {"title": title})
            course.title = title
        return course

    async def update_course(self, course_id: int, values: dict) -> None:
        await self.session.execute(
            update(CoursesOrm)
            .filter_by(id=course_id)
            .values(
                **values,
                updated_at=func.now(),
            )
        )

    async def delete_course(self, course_id: int) -> None:
        await self.session.execute(
            update(CoursesOrm)
            .filter_by(id=course_id)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )

    async def attach_course(self, student_id: int, course_id: int) -> None:
        await self._acquire_advisory_lock(f"course-links:{course_id}")
        await self.session.execute(
            insert(StudentsCoursesOrm)
            .values(
                student_id=student_id,
                course_id=course_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    StudentsCoursesOrm.student_id,
                    StudentsCoursesOrm.course_id,
                ]
            )
        )

    async def detach_course(self, student_id: int, course_id: int) -> None:
        await self._acquire_advisory_lock(f"course-links:{course_id}")
        await self.session.execute(
            delete(StudentsCoursesOrm).filter_by(
                student_id=student_id,
                course_id=course_id,
            )
        )

    async def delete_course_if_unused(self, course_id: int) -> None:
        await self._acquire_advisory_lock(f"course-links:{course_id}")
        await self.session.execute(
            update(CoursesOrm)
            .where(
                CoursesOrm.id == course_id,
                CoursesOrm.is_deleted.is_(False),
                ~exists().where(StudentsCoursesOrm.course_id == CoursesOrm.id),
            )
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
        )
