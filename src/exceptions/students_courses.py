from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.schemas.errors import StudentErrorDetails


class StudentNotFoundException(ObjectNotFoundException):
    message = "Student not found"

    def __init__(self, *, student_id: int):
        super().__init__(
            details=StudentErrorDetails(student_id=student_id),
        )


class StudentAlreadyExistsException(AlreadyExistsException):
    message = "A student with this record book number already exists"

    def __init__(self, *, record_book_number: str):
        super().__init__(
            details=StudentErrorDetails(record_book_number=record_book_number),
        )
