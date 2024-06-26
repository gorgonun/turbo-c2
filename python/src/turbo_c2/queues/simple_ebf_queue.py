from typing import Any, Iterable, TypeVar
from turbo_c2.exceptions.exceptions import EmptyQueueException
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T")


class SimpleEbfQueue(EBFQueue[T]):
    def __init__(self, definition: QueueDefinition):
        self.queue: list[Any] = []
        super().__init__(definition)

    async def put(self, data: T):
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

    async def get(self):
        try:
            result = self.queue.pop(0)
        except IndexError:
            raise EmptyQueueException
        return result
    
    async def get_iter(self, count: int):
        if count > len(self.queue):
            count = len(self.queue)
        data = self.queue[:count]
        self.queue = self.queue[count:]
        return data

    async def qsize(self):
        return len(self.queue)
    
    def __iter__(self):
        return iter(self.queue)
