from typing import Type, TypeVar

from pydantic import BaseModel

from turbo_c2.helpers.serde.pydantic_serde import DefaultPydanticSerDe


T = TypeVar("T", bound=BaseModel)


def dynamic_pydantic_serde(serde_t: Type[T]):
    class DynamicPydanticSerde(DefaultPydanticSerDe[T]):
        element_type = serde_t
    
    return DynamicPydanticSerde
