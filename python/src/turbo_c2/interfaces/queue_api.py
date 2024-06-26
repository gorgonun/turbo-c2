import abc
from typing import Any, Generator, Generic, Iterable, TypeVar

from turbo_c2.queues.queue_controller import QueueController


T = TypeVar("T", bound=QueueController)


class QueueApi(abc.ABC, Generic[T]):
    @abc.abstractmethod
    async def get_queue_name(self) -> str:
        pass

    @abc.abstractmethod
    async def put(self, data: T, consumer_name: str | None = None) -> None:
        pass
    
    @abc.abstractmethod
    async def put_data(self, data: T) -> None:
        pass

    @abc.abstractmethod
    async def put_iter(self, data: Iterable[T]) -> int:
        pass

    @abc.abstractmethod
    async def get(self, consumer_name: str | None = None, wait: bool | None = None) -> T:
        pass
    
    @abc.abstractmethod
    async def get_data(self):
        pass

    @abc.abstractmethod
    async def get_iter(self, count: int, consumer_name: str | None = None) -> list[T]:
        pass

    @abc.abstractmethod
    async def qsize(self) -> int:
        pass

    @abc.abstractmethod
    async def wait(self, timeout: int | None = None):
        pass
    
    @abc.abstractmethod
    async def geti(self, consumer_name: str | None = None) -> Generator[Any, Any, None]:
        pass

    @abc.abstractmethod
    def __aiter__(self) -> T:
        pass

    @abc.abstractmethod
    async def __anext__(self) -> T:
        pass

    @abc.abstractmethod
    async def unregister(self, consumer_name: str):
        pass

    @abc.abstractmethod
    async def finish(self, consumer_name: str | None = None):
        pass

    @abc.abstractmethod
    async def register(self, consumer_name: str):
        pass
