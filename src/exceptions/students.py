from src.exceptions.base import ConflictError, NotFoundError


class StudentNotFoundError(NotFoundError):
    code = "student_not_found_error"
    message = "Студент не найден"

class StudentConflictError(ConflictError):
    code = "student_conflict_error"
    message = "Студент уже существует"


