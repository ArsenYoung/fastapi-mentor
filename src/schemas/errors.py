from typing import Any, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(description="Error message")
    details: Mapping[str, Any] | Sequence[Any] | str | None = None

class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    error: ErrorPayload
