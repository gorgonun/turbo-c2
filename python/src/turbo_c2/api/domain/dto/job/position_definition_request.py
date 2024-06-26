from pydantic import BaseModel


class MovePositionDefinitionRequest(BaseModel):
    x: float
    y: float


class PositionDefinitionRequest(BaseModel):
    position_definition: MovePositionDefinitionRequest
    element_type: str
