from pydantic import BaseModel


class ScaleJobRequest(BaseModel):
    replicas: int
