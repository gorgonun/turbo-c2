from typing import Iterable, TypeVar
import uuid
from turbo_c2.exceptions.exceptions import EmptyQueueException
from turbo_c2.queues.ebf_queue import EBFQueue


T = TypeVar("T")


class InMemoryQueue(EBFQueue[T]):
    def __init__(self, name: str|None=None):
        self.queue: list[T] = []
        super().__init__(name or uuid.uuid4())

    async def put(self, data: T) -> None:
        self.queue.append(data)

    async def put_iter(self, data: Iterable[T]) -> None:
        if isinstance(data, list):
            self.queue.extend(data)
            return len(data)
        else:
            count = 0
            for item in data:
                self.queue.append(item)
                count += 1
            return count

    async def get(self) -> T:
        try:
            return self.queue.pop(0)
        except IndexError:
            raise EmptyQueueException()
        
    async def get_iter(self, count: int) -> list[T]:
        if count > len(self.queue):
            count = len(self.queue)
        data = self.queue[:count]
        self.queue = self.queue[count:]
        return data

    async def qsize(self) -> int:
        return len(self.queue)
