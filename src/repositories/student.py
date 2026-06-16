from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

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
                selectinload(StudentsOrm.course_link).joinedload(
                    StudentsCoursesOrm.courses.and_(CoursesOrm.is_deleted.is_(False))
                )
            )
            .order_by(StudentsOrm.id)
        )

    async def _get_student_with_courses(self, student_id: int) -> StudentsOrm | None:
        stmt = self._get_with_courses_stmt().where(StudentsOrm.id == student_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_student_by_record_book_number(
        self,
        record_book_number: str,
    ) -> StudentsOrm | None:
        stmt = select(StudentsOrm).where(
            StudentsOrm.record_book_number == record_book_number,
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
