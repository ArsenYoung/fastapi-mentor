from sqlalchemy.exc import IntegrityError

from src.models.students import StudentsOrm
from src.repositories.student import StudentRepository
from src.schemas.students import StudentCreateRequest, StudentPatch
from src.services.base import BaseService


class StudentService(BaseService):
    student_not_found_msg = "Student not found"
    student_already_exists_msg = "A student with this record book number already exists"
    student_unique_constraint = "uq_students_record_book_number_active"

    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def _is_student_unique_error(self, exc: IntegrityError) -> bool:
        return self.student_unique_constraint in str(exc)

    async def get_active_by_id_or_raise(self, student_id: int) -> StudentsOrm:
        student = await self.repo.get_by_id_active(student_id)
        if student is None:
            self._raise_not_found(
                message=self.student_not_found_msg,
                student_id=student_id
            )
        return student

    async def get_any_by_record_book_number(self, record_book_number: str) -> StudentsOrm | None:
        return await self.repo.get_any_by_record_book_number(record_book_number)

    async def ensure_record_book_number_available_for_create(
        self,
        record_book_number: str,
    ) -> None:
        student = await self.get_any_by_record_book_number(record_book_number)
        if student is not None:
            self._raise_already_exists(
                message=self.student_already_exists_msg,
                record_book_number=record_book_number,
            )

    async def get_page(self, limit: int, offset: int) -> tuple[list[StudentsOrm], int]:
        return await self.repo.get_page(limit, offset)
    
    async def create_or_restore(self, data: StudentCreateRequest) -> StudentsOrm:
        student = await self.get_any_by_record_book_number(data.record_book_number)
        if student is None:
            return await self.create(data)
        if student.is_deleted:
            await self.restore(student.id)
            await self.update(
                student.id,
                StudentPatch(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    record_book_number=data.record_book_number,
                )
            )
            return await self.get_active_by_id_or_raise(student.id)
        self._raise_already_exists(
            message=self.student_already_exists_msg,
            record_book_number=data.record_book_number,
        )

    async def create(self, data: StudentCreateRequest) -> StudentsOrm:
        try:
            return await self.repo.insert(
                first_name=data.first_name,
                last_name=data.last_name,
                record_book_number=data.record_book_number,
            )
        except IntegrityError as exc:
            if self._is_student_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.student_already_exists_msg,
                    record_book_number=data.record_book_number
                )
            raise

    async def update(self, student_id: int, data: StudentPatch) -> None:
        await self.get_active_by_id_or_raise(student_id)
        values = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"courses"},
        )
        if not values:
            return
        try:
            await self.repo.update(student_id, values)
        except IntegrityError as exc:
            if self._is_student_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.student_already_exists_msg,
                    student_id=student_id,
                    record_book_number=data.record_book_number,
                )
            raise

    async def soft_delete(self, student_id: int) -> None:
        await self.get_active_by_id_or_raise(student_id)
        await self.repo.soft_delete(student_id)

    async def restore(self, student_id: int) -> None:
        student = await self.repo.get_by_id_any(student_id)
        if student is None:
            self._raise_not_found(
               message=self.student_not_found_msg, 
               student_id=student_id
            )
        try:
            await self.repo.restore(student_id)
        except IntegrityError as exc:
            if self._is_student_unique_error(exc):
                self._raise_already_exists(
                    exc,
                    message=self.student_already_exists_msg,
                    student_id=student_id,
                    record_book_number=student.record_book_number,
                )
            raise
