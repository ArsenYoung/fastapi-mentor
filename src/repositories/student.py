from typing import Sequence

from sqlalchemy import select

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentsOrm]):
    model = StudentsOrm

    async def get_courses_by_reestr_numbers(
        self,
        reestr_numbers: Sequence[str],
        *,
        for_update: bool = False,
    ) -> list[CoursesOrm]:
        stmt = (
            select(CoursesOrm)
            .where(
                CoursesOrm.is_deleted.is_(False),
                CoursesOrm.reestr_number.in_(reestr_numbers),
            )
            .order_by(CoursesOrm.reestr_number)
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_course_ids_with_active_students(
        self,
        courses: set[CoursesOrm],
    ) -> set[int]:
        course_ids = {course.id for course in courses if course.id is not None}
        if not course_ids:
            return set()

        stmt = (
            select(StudentsCoursesOrm.course_id)
            .join(StudentsOrm, StudentsCoursesOrm.student_id == StudentsOrm.id)
            .where(
                StudentsCoursesOrm.course_id.in_(course_ids),
                StudentsOrm.is_deleted.is_(False),
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())
