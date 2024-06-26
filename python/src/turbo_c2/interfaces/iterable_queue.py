import abc
from typing import Generic, TypeVar


T = TypeVar("T")


class IterableQueue(Generic[T], abc.ABC):
    @abc.abstractmethod
    async def get(self) -> T:
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    async def __next__(self):
        pass
