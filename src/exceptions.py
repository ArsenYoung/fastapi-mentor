class AppError(Exception):
    code = "unexpected_error"
    message = "Неизвестная ошибка"
    details = None

class NotFoundError(AppError):
    code = "object_not_found_error"
    message = "Объект не найден"


class ConflictError(AppError):
    code = "conflict_error"
    message = "Конфликт"


class AuthorNotFoundError(NotFoundError):
    code = "author_not_found_error"
    message = "Автор не найден"


class AuthorConflictError(ConflictError):
    code = "author_conflict_error"
    message = "Автор с таким именем уже существует"


class PersonNotFoundError(NotFoundError):
    code = "person_not_found_error"
    message = "Человек не найден"


class PassportConflictError(ConflictError):
    code = "passport_conflict_error"
    message = "Номер паспорта уже существует"
