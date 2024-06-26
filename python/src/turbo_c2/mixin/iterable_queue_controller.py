import abc
from typing import Any, Generic, TypeVar
from turbo_c2.exceptions.exceptions import EmptyQueueException
from turbo_c2.interfaces.iterable_queue import IterableQueue


# Remote queue reference
T = TypeVar("T", bound=IterableQueue)


class IterableQueueController(Generic[T], abc.ABC):
    def __init__(self, queue: T):
        self.__queue = queue

    async def get(self) -> Any:
        return await self.__queue.get()

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.get()
        except EmptyQueueException:
            raise StopAsyncIteration
