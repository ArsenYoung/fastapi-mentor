from pydantic import BaseModel, ConfigDict, Field


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: dict | list | str | None = None

class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    error: ErrorPayload