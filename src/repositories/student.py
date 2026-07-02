from typing import Mapping

from sqlalchemy import select

from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentsOrm]):
    model = StudentsOrm

    async def create_course(self, course: CoursesOrm) -> CoursesOrm:
        self.session.add(course)
        await self.session.flush()
        return course

    async def update_course(
        self,
        course: CoursesOrm,
        values: Mapping[str, object],
    ) -> CoursesOrm:
        for field, value in values.items():
            setattr(course, field, value)
        return course

    async def delete_course(self, course: CoursesOrm) -> None:
        course.is_deleted = True

    async def get_course_by_reestr_number(
        self,
        reestr_number: str,
    ) -> CoursesOrm | None:
        stmt = select(CoursesOrm).where(
            CoursesOrm.is_deleted.is_(False),
            CoursesOrm.reestr_number == reestr_number,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def attach_course(
        self,
        student: StudentsOrm,
        course: CoursesOrm,
    ) -> None:
        if course.id not in {existing_course.id for existing_course in student.courses}:
            student.courses.append(course)
            await self.session.flush()

    async def detach_course(
        self,
        student: StudentsOrm,
        course: CoursesOrm,
    ) -> None:
        for existing_course in list(student.courses):
            if existing_course.id == course.id:
                student.courses.remove(existing_course)
                await self.session.flush()
                return

    async def course_has_active_students(self, course: CoursesOrm) -> bool:
        stmt = (
            select(StudentsCoursesOrm)
            .join(StudentsOrm, StudentsCoursesOrm.student_id == StudentsOrm.id)
            .where(
                StudentsCoursesOrm.course_id == course.id,
                StudentsOrm.is_deleted.is_(False),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.first() is not None
