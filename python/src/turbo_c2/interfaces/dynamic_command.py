from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")
U = TypeVar("U")


@dataclass
class DynamicCommand(Generic[T, U]):
    api_identifier: str
    api_path: str

    @property
    def args(self):
        return []
    
    @property
    def kwargs(self):
        return {}
