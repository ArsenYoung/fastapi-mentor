from src.models.students import StudentsOrm
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository):
    model = StudentsOrm

    def __init__(self, session):
        self.session = session
    
    async def get_any_by_record_book_number(self, record_book_number: str) -> StudentsOrm | None:
        return await self.get_latest_one(
            StudentsOrm,
            StudentsOrm.id,
            record_book_number=record_book_number,
        )
    
    async def insert(
        self,
        first_name: str,
        last_name: str,
        record_book_number: str,
    ) -> StudentsOrm:
        return await self.insert_model(
            first_name=first_name,
            last_name=last_name,
            record_book_number=record_book_number,
        )
