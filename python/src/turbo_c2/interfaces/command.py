from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar


T = TypeVar("T")
U = TypeVar("U")


@dataclass
class Command(Generic[T, U]):
    api_identifier: ClassVar[str]
    api_path: ClassVar[str]

    @property
    def args(self):
        return []
    
    @property
    def kwargs(self):
        return {}
