from pydantic import BaseModel


class CommonResponse(BaseModel):
    status: str = "ok"