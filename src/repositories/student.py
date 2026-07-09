from typing import Sequence

from sqlalchemy import false, select
from sqlalchemy.dialects.postgresql import insert

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentsOrm]):
    model = StudentsOrm

    async def create_courses_do_nothing(
        self,
        courses: Sequence[tuple[str, str]],
    ) -> None:
        if not courses:
            return

        stmt = (
            insert(CoursesOrm)
            .values(
                [
                    {
                        "reestr_number": reestr_number,
                        "title": title,
                    }
                    for reestr_number, title in courses
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[CoursesOrm.reestr_number],
                index_where=CoursesOrm.is_deleted == false(),
            )
        )
        await self.session.execute(stmt)

    async def create_student_course_links_do_nothing(
        self,
        student_id: int,
        course_ids: Sequence[int],
    ) -> None:
        if not course_ids:
            return

        stmt = (
            insert(StudentsCoursesOrm)
            .values(
                [
                    {
                        "student_id": student_id,
                        "course_id": course_id,
                    }
                    for course_id in course_ids
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[
                    StudentsCoursesOrm.student_id,
                    StudentsCoursesOrm.course_id,
                ],
            )
        )
        await self.session.execute(stmt)

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

    async def lock_courses_by_ids(self, course_ids: Sequence[int]) -> None:
        if not course_ids:
            return

        stmt = (
            select(CoursesOrm.id)
            .where(CoursesOrm.id.in_(course_ids))
            .with_for_update()
        )
        await self.session.execute(stmt)

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
