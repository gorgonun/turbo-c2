from typing import Generic, Type, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class PydanticSerDe(Generic[T]):
    @classmethod
    def to_dict(cls, element: T) -> dict:
        return element.model_dump()

    @classmethod
    def serialize(cls, element: T) -> str:
        return element.model_dump_json()
    
    @classmethod
    def from_dict(cls, element: Type[T], element_dict: dict) -> T:
        return element(**element_dict)

    @classmethod
    def deserialize(cls, element: Type[T], element_json: str) -> T:
        return element.model_validate_json(element_json)


class DefaultPydanticSerDe(PydanticSerDe[T]):
    element_type: Type[T]

    @classmethod
    def from_dict(cls, element_dict: dict) -> T:
        return PydanticSerDe.from_dict(cls.element_type, element_dict)
    
    @classmethod
    def deserialize(cls, element_json: str) -> T:
        return PydanticSerDe.deserialize(cls.element_type, element_json)
