from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(description="Error message")
    details: Dict | List | str | None = None

class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    error: ErrorPayload
