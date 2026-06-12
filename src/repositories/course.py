from src.models.courses import CoursesOrm
from src.repositories.base import BaseRepository


class CourseRepository(BaseRepository):
    model = CoursesOrm

    def __init__(self, session):
        self.session = session

    async def get_by_reestr_number(self, reestr_number: str) -> CoursesOrm | None:
        return await self.get_latest_one(
            CoursesOrm,
            CoursesOrm.id,
            reestr_number=reestr_number,
        )
    
    async def get_by_ids(self, course_ids: list[int]) -> list[CoursesOrm]:
        return await self.get_many_active_in(
            CoursesOrm,
            CoursesOrm.id,
            course_ids,
            order_by=CoursesOrm.id
        )
    
    async def insert(self, reestr_number: str, title: str) -> CoursesOrm:
        return await self.insert_model(
            reestr_number=reestr_number,
            title=title,
        )
