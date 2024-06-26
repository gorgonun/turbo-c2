import abc
from typing import Generic, Iterable, TypeVar
import uuid

from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T")


class EBFQueue(Generic[T], abc.ABC):
    def __init__(self, definition: QueueDefinition) -> None:
        self.name = definition.name or self.__class__.__name__ + "_" + uuid.uuid4().hex[:8]  # type: ignore

    @abc.abstractmethod
    async def put(self, data: T) -> None:
        pass

    @abc.abstractmethod
    async def put_iter(self, data: Iterable[T]) -> int:
        """
        Put multiple data into the queue and returns the number of data added.
        """
        pass

    @abc.abstractmethod
    async def get(self) -> T:
        pass

    @abc.abstractmethod
    async def get_iter(self, count: int) -> list[T]:
        """
        Get multiple data from the queue and returns a list of data.
        """
        pass

    @abc.abstractmethod
    async def qsize(self) -> int:
        pass

    async def get_name(self) -> str:
        return self.name

    @abc.abstractmethod
    def __iter__(self):
        pass
