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