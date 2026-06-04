from src.exceptions.base import ConflictError, NotFoundError


class PassportNotFoundError(NotFoundError):
    code = "passport_not_found_error"
    message = "Паспорт не найден"

class PassportConflictError(ConflictError):
    code = "passport_conflict_error"
    message = "Номер паспорта уже существует"