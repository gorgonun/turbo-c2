import abc
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass
class HasId(abc.ABC):
    @property
    @abc.abstractmethod
    def resource_id(self) -> str:
        pass

    def __hash__(self):
        return hash(self.resource_id)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.resource_id == getattr(o, "resource_id")
        return False
