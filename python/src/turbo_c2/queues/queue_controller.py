import abc
import asyncio
from typing import Any, Generator, Generic, Iterable, TypeVar
from turbo_c2.helpers.event_utils import EventUtils
from turbo_c2.exceptions.exceptions import EmptyQueueException
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T", bound=EBFQueue)


class QueueController(Generic[T], abc.ABC):
    def __init__(
        self,
        queue: T,
        queue_definition: QueueDefinition,
        name: str | None = None,
        strict_consumers: list[str] | None = None,
        wait_data_event: asyncio.Event | None = None,
        finished_event: asyncio.Event | None = None,
    ) -> None:
        self.__queue = queue
        self.__name = name or NameUtils.get_anonymous_name("QueueController")
        self.__strict_consumers = set(strict_consumers or [])
        self.__finished_wait_data_combined = EventUtils.combine_events(
            {
                "finished_event": finished_event,
                "wait_data_event": wait_data_event,
            }
        )
        self.__logger = TurboLogger(name or self.__class__.__name__)
        self.__queue_definition = queue_definition

    @property
    def queue(self) -> T:
        return self.__queue

    @property
    def name(self) -> str:
        return self.__name

    @property
    def finished_event(self) -> asyncio.Event:
        return self.__finished_wait_data_combined["finished_event"]

    @property
    def wait_data_event(self) -> asyncio.Event:
        return self.__finished_wait_data_combined["wait_data_event"]

    @property
    def strict_consumers(self) -> set[str]:
        return self.__strict_consumers
    
    @property
    def queue_definition(self) -> QueueDefinition:
        return self.__queue_definition
    
    @property
    def queue_name(self) -> str:
        return self.__queue_definition.name

    def set_finished_event(self):
        self.__finished_wait_data_combined.set_event("finished_event")

    def set_wait_data_event(self):
        self.__finished_wait_data_combined.set_event("wait_data_event")

    async def put(self, data: T, consumer_name: str | None = None) -> None:
        self.__logger.debug("QueueController - put")
        if self.finished_event.is_set():
            raise RuntimeError(f"Cannot put data into a finished queue {self.name}")

        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to put into queue {self.name}"
            )

        self.__logger.debug("Putting on queue")

        return await self.put_data(data)
    
    async def put_iter(self, data: Iterable[T], consumer_name: str | None = None) -> None:
        self.__logger.debug("QueueController - put_iter")
        if self.finished_event.is_set():
            raise RuntimeError(f"Cannot put data into a finished queue {self.name}")

        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to put into queue {self.name}"
            )

        self.__logger.debug("Putting on queue")

        return await self.put_data_iter(data)

    async def put_data(self, data: T) -> None:
        result = await self.__queue.put(data)
        self.set_wait_data_event()
        return result
    
    async def put_data_iter(self, data: Iterable[T]):
        result = await self.__queue.put_iter(data)
        self.set_wait_data_event()
        return result

    async def get(
        self, consumer_name: str | None = None, wait: bool | None = None
    ) -> T:
        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to pop from queue {self.name}"
            )

        self.__logger.debug("getting data")
        if wait:
            await self.wait()

        if self.finished_event.is_set():
            raise RuntimeError(f"Cannot get data from a finished queue {self.name}")

        result = await self.get_data()
        if await self.qsize() == 0:
            self.wait_data_event.clear()

        return result

    async def get_data(self):
        return await self.__queue.get()
    
    async def get_data_iter(self, count: int):
        return await self.__queue.get_iter(count)
    
    async def get_iter(self, count: int, consumer_name: str | None = None) -> list[T]:
        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to pop from queue {self.name}"
            )

        self.__logger.debug("getting data")
        if self.finished_event.is_set() and await self.qsize() == 0:
            raise EmptyQueueException()

        result = await self.get_data_iter(count)
        if await self.qsize() == 0:
            self.wait_data_event.clear()

        return result

    async def qsize(self) -> int:
        return await self.__queue.qsize()

    async def wait(self, timeout: int | None = None):
        # Wait one item to be available or the queue to be finished
        return await self.__finished_wait_data_combined.wait_any_set(timeout)

    async def geti(self, consumer_name: str | None = None) -> Generator[Any, Any, None]:
        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to iterate over queue {self.name}"
            )

        ai_self = aiter(self)
        while True:
            try:
                yield await anext(ai_self)
            except StopAsyncIteration:
                break

    def __aiter__(self):
        if self.__strict_consumers:
            raise RuntimeError(
                "Cannot iterate over a queue with strict consumers. Use geti instead."
            )

        return self

    async def __anext__(self):
        try:
            return await self.get()
        except EmptyQueueException:
            raise StopAsyncIteration

    async def unregister(self, consumer_name: str):
        if self.__strict_consumers:
            self.__strict_consumers.remove(consumer_name)

    async def finish(self, consumer_name: str | None = None):
        if self.__strict_consumers and consumer_name not in self.__strict_consumers:
            raise RuntimeError(
                f"Consumer {consumer_name} is not allowed to finish queue {self.name}"
            )

        if (
            len(self.__strict_consumers) == 1
            and consumer_name in self.__strict_consumers
        ):
            self.__strict_consumers.remove(consumer_name)

        if self.__strict_consumers:
            raise RuntimeError(
                f"Cannot finish queue {self.name} because there are still consumers left."
            )

        self.set_finished_event()

    async def register(self, consumer_name: str):
        self.__strict_consumers.add(consumer_name)
