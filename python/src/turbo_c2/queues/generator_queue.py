from typing import Callable, Generator, TypeVar
import uuid
from turbo_c2.exceptions.exceptions import EmptyQueueException
from turbo_c2.interfaces.iterable_queue import IterableQueue


T = TypeVar("T")


class GeneratorQueue(IterableQueue[T]):
    def __init__(self, generator_function: Callable[[], Generator[T]], name: str|None=None):
        self.__generator = generator_function()
        self.__name = name or uuid.uuid4()

    @property
    def name(self):
        return self.__name
    
    async def get(self) -> T:
        return next(self.__generator)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.get()
        except IndexError:
            raise EmptyQueueException()
