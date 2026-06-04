from src.exceptions.base import ConflictError, NotFoundError


class CourseNotFoundError(NotFoundError):
    code = "course_not_found_error"
    message = "Курс не найден"

class CourseConflictError(ConflictError):
    code = "course_conflict_error"
    message = "Курс уже существует"