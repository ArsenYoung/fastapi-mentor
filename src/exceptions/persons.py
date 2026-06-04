from src.exceptions.base import NotFoundError


class PersonNotFoundError(NotFoundError):
    code = "person_not_found_error"
    message = "Человек не найден"