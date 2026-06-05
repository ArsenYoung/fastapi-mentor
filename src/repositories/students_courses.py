from collections.abc import Iterable

from sqlalchemy import select
from src.models.courses import CoursesOrm
from src.models.students import StudentsOrm
from src.models.students_courses import StudentsCoursesOrm
from src.repositories.base import BaseRepository


class StudentsCoursesRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_student(self, student_id: int) -> StudentsOrm | None:
        return await self.fetch_active_one(
            StudentsOrm, 
            id=student_id
        )

    async def get_student_by_record_book_number(self, record_book_number: str) -> StudentsOrm | None:
        stmt = (
            select(StudentsOrm)
            .filter_by(record_book_number=record_book_number)
            .order_by(StudentsOrm.id.desc())
        )
        return await self.fetch_one(stmt)

    async def get_student_links(self, student_id: int) -> list[StudentsCoursesOrm]:
        return await self.fetch_active_all(
            StudentsCoursesOrm, 
            student_id=student_id
        )

    async def get_students_links(self, student_ids: Iterable[int]) -> list[StudentsCoursesOrm]:
        return await self.fetch_active_in(
            StudentsCoursesOrm,
            StudentsCoursesOrm.student_id,
            student_ids,
        )
    
    async def get_students_page(self, limit: int, offset: int) -> tuple[list[StudentsOrm], int]:
        return await self.fetch_active_page(
            StudentsOrm,
            limit=limit,
            offset=offset,
            order_by=StudentsOrm.id
        )
    
    async def get_course_by_reestr_number(self, reestr_number: str) -> CoursesOrm | None:
        stmt = (
            select(CoursesOrm)
            .filter_by(reestr_number=reestr_number)
            .order_by(CoursesOrm.id.desc())
        )
        return await self.fetch_one(stmt)
    
    async def get_courses_by_ids(self, course_ids: list[int]) -> list[CoursesOrm]:
        return await self.fetch_active_in(
            CoursesOrm,
            CoursesOrm.id,
            course_ids,
            order_by=CoursesOrm.id
        )
    
    async def insert_course(self, reestr_number: str, title: str) -> CoursesOrm:
        return await self.insert_instance(
            CoursesOrm(
                reestr_number=reestr_number,
                title=title,
            )
        )
    
    async def insert_student(
        self,
        first_name: str,
        last_name: str,
        record_book_number: str,
    ) -> StudentsOrm:
        return await self.insert_instance(
            StudentsOrm(
                first_name=first_name,
                last_name=last_name,
                record_book_number=record_book_number,
            )
        )

    async def restore_student(self, student_id: int) -> None:
        await self.update_where(
            StudentsOrm,
            {"is_deleted": False},
            id=student_id
        )
    
    async def restore_course(self, course_id: int) -> None:
        await self.update_where(
            CoursesOrm,
            {"is_deleted": False},
            id=course_id
        )

    async def attach_course_to_student(self, student_id: int, course_id: int) -> None:
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

    async def detach_course_from_student(self, student_id: int, course_id: int) -> None:
        await self.soft_delete_where(
            StudentsCoursesOrm,
            student_id=student_id,
            course_id=course_id,
        )

    async def soft_delete_course_if_orphan(self, course_id: int) -> None:
        active_link = await self.fetch_active_one(
            StudentsCoursesOrm,
            course_id=course_id,
        )
        if active_link is None:
            await self.soft_delete_where(
                CoursesOrm,
                id=course_id,
            )

    async def soft_delete_student(self, student_id: int) -> None:
        student = await self.fetch_active_one(
            StudentsOrm,
            id=student_id,
        )
        if student is not None:
            await self.soft_delete_where(
                StudentsOrm,
                id=student_id,
            )

    async def update_course(self, course_id: int, values: dict) -> None:
        await self.update_where(
            CoursesOrm,
            values,
            id=course_id
        )

    async def update_student(self, student_id: int, values: dict) -> None:
        await self.update_where(
            StudentsOrm,
            values,
            id=student_id
        )
