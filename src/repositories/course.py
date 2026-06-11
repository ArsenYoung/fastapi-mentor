from sqlalchemy import select

from src.models.courses import CoursesOrm
from src.repositories.base import BaseRepository


class CourseRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_reestr_number(self, reestr_number: str) -> CoursesOrm | None:
        stmt = (
            select(CoursesOrm)
            .filter_by(reestr_number=reestr_number)
            .order_by(CoursesOrm.id.desc())
        )
        return await self.fetch_one(stmt)
    
    async def get_by_ids(self, course_ids: list[int]) -> list[CoursesOrm]:
        return await self.fetch_active_in(
            CoursesOrm,
            CoursesOrm.id,
            course_ids,
            order_by=CoursesOrm.id
        )
    
    async def insert(self, reestr_number: str, title: str) -> CoursesOrm:
        return await self.insert_instance(
            CoursesOrm(
                reestr_number=reestr_number,
                title=title,
            )
        )
    
    async def restore(self, course_id: int) -> None:
        await self.update_where(
            CoursesOrm,
            {"is_deleted": False},
            id=course_id
        )

    async def soft_delete(self, course_id: int) -> None:
        await self.soft_delete_where(
            CoursesOrm,
            id=course_id,
        )

    async def update(self, course_id: int, values: dict) -> None:
        await self.update_where(
            CoursesOrm,
            values,
            id=course_id
        )

    async def get_by_id_any(self, course_id: int) -> CoursesOrm | None:
        return await self.fetch_one(
            select(CoursesOrm)
            .filter_by(id=course_id)
        )