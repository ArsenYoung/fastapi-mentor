from src.exceptions.base import ConflictError, NotFoundError


class AuthorNotFoundError(NotFoundError):
    code = "author_not_found_error"
    message = "Автор не найден"

class AuthorConflictError(ConflictError):
    code = "author_conflict_error"
    message = "Автор с таким именем уже существует"