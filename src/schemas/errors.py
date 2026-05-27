from pydantic import BaseModel, ConfigDict, Field


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')
    code: str = Field(description="unexpected_error")
    message: str = Field(description="Неизвестная ошибка")
    details: dict | list | str | None = None

class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    error: ErrorPayload

class NotFoundError(ErrorPayload):
    code: str = Field(description="object_not_found_error")
    message: str = Field(description="Объект не найден")

class ConflictError(ErrorPayload):
    code: str = Field(description="conflict_error")
    message: str = Field(description="Такой объект уже существует")

class AuthorNotFoundError(NotFoundError):
    code: str = Field(description="author_not_found_error")
    message: str = Field(default="Автор не найден", description="Автор не найден")

class AuthorConflictError(ConflictError):
    code: str = Field(description="author_conflict_error")
    message: str = Field(default="Автор с таким именем уже существует", description="Автор с таким именем уже существует")