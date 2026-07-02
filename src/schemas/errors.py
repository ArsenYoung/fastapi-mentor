from pydantic import BaseModel, ConfigDict, Field


class ErrorDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthorErrorDetails(ErrorDetails):
    author_code: str | None = None
    author_id: int | None = None


class BookErrorDetails(ErrorDetails):
    book_code: str | None = None


class CourseErrorDetails(ErrorDetails):
    reestr_number: str | None = None


class PassportErrorDetails(ErrorDetails):
    passport_number: str | None = None


class PersonErrorDetails(ErrorDetails):
    person_id: int | None = None


class StudentErrorDetails(ErrorDetails):
    record_book_number: str | None = None
    student_id: int | None = None


ErrorDetailsType = (
    AuthorErrorDetails
    | BookErrorDetails
    | CourseErrorDetails
    | PassportErrorDetails
    | PersonErrorDetails
    | StudentErrorDetails
    | None
)


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(description="Error message")
    details: ErrorDetailsType = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: ErrorPayload
