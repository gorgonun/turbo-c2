from pydantic import BaseModel


class CreateJobGroupRequest(BaseModel):
    name: str
    path: str
    description: str | None
    read_only: bool = False
    meta: dict[str, str] | None = None
