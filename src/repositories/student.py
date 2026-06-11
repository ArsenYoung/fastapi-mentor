from sqlalchemy import select

from src.models.students import StudentsOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_by_id_active(self, student_id: int) -> StudentsOrm | None:
        return await self.fetch_active_one(
            StudentsOrm, 
            id=student_id
        )
    
    async def get_by_id_any(self, student_id: int) -> StudentsOrm | None:
        return await self.fetch_one(
            select(StudentsOrm)
            .filter_by(id=student_id)
        )
    
    async def get_any_by_record_book_number(self, record_book_number: str) -> StudentsOrm | None:
        stmt = (
            select(StudentsOrm)
            .filter_by(record_book_number=record_book_number)
            .order_by(StudentsOrm.id.desc())
        )
        return await self.fetch_one(stmt)
    
    async def get_page(self, limit: int, offset: int) -> tuple[list[StudentsOrm], int]:
        return await self.fetch_active_page(
            StudentsOrm,
            limit=limit,
            offset=offset,
            order_by=StudentsOrm.id
        )
    
    async def insert(
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
    
    async def update(self, student_id: int, values: dict) -> None:
        await self.update_where(
            StudentsOrm,
            values,
            id=student_id
        )

    async def soft_delete(self, student_id: int) -> None:
        await self.soft_delete_where(
                StudentsOrm,
                id=student_id,
            )

    async def restore(self, student_id: int) -> None:
        await self.update_where(
            StudentsOrm,
            {"is_deleted": False},
            id=student_id
        )