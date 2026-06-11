from collections.abc import Iterable

from sqlalchemy import select
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentsCoursesRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_links_by_student_id(self, student_id: int) -> list[StudentsCoursesOrm]:
        return await self.fetch_active_all(
            StudentsCoursesOrm, 
            student_id=student_id
        )

    async def get_links_by_students_ids(self, student_ids: Iterable[int]) -> list[StudentsCoursesOrm]:
        return await self.fetch_active_in(
            StudentsCoursesOrm,
            StudentsCoursesOrm.student_id,
            student_ids,
        )

    async def attach(self, student_id: int, course_id: int) -> None:
        existing_link = await self.fetch_one(
            select(StudentsCoursesOrm).filter_by(
                student_id=student_id,
                course_id=course_id,
            )
        )

        if existing_link is None:
            await self.insert_instance(
                StudentsCoursesOrm(
                    student_id=student_id,
                    course_id=course_id,
                )
            )
            return
        
        if existing_link.is_deleted:
            await self.update_where(
                StudentsCoursesOrm,
                {"is_deleted": False},
                student_id=student_id,
                course_id=course_id,
            )

    async def detach(self, student_id: int, course_id: int) -> None:
        await self.soft_delete_where(
            StudentsCoursesOrm,
            student_id=student_id,
            course_id=course_id,
        )

    async def has_active_links(self, course_id: int) -> bool:
        active_link = await self.fetch_active_one(
            StudentsCoursesOrm,
            course_id=course_id,
        )
        return active_link is not None

    
