import asyncio
from typing import Iterable, TypeVar

from turbo_c2.queues.remote_queue_controller import RemoteQueueController
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.queue_api import QueueApi


T = TypeVar("T", bound=RemoteQueueController)


class RemoteQueueApi(QueueApi[T]):
    def __init__(self, queue_controller: T) -> None:
        if not queue_controller:
            raise RuntimeError("queue_controller is None")

        self.__queue_controller = queue_controller
        self.__logger = TurboLogger("RemoteQueueApi")

    async def get_queue_name(self) -> str:
        self.__logger.debug("api - get name")
        self.__logger.debug(self.__queue_controller)
        return await self.__queue_controller.get_queue_name.remote()

    async def put(self, data: T, consumer_name: str | None = None) -> None:
        self.__logger.debug("api - put", self.__queue_controller)
        return await self.__queue_controller.put.remote(data, consumer_name)

    async def put_data(self, data: T) -> None:
        return await self.__queue_controller.put_data.remote(data)
    
    async def put_iter(self, data: Iterable[T]) -> int:
        return await self.__queue_controller.put_iter.remote(data)

    async def get(
        self, consumer_name: str | None = None, wait: bool | None = None
    ) -> T:
        return await self.__queue_controller.get.remote(consumer_name, wait)
    
    async def get_iter(self, count: int, consumer_name: str | None = None) -> list[T]:
        return await self.__queue_controller.get_iter.remote(count, consumer_name)

    async def get_data(self):
        return await self.__queue_controller.get_data.remote()

    async def qsize(self) -> int:
        return await self.__queue_controller.qsize.remote()

    async def wait(self, timeout: int | None = None):
        return await self.__queue_controller.wait.remote(timeout)

    async def geti(self, consumer_name: str | None = None):
        return await self.__queue_controller.geti.remote(consumer_name)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.__queue_controller.__anext__.remote()

    async def unregister(self, consumer_name: str):
        return await self.__queue_controller.unregister.remote(consumer_name)

    async def register(self, consumer_name: str):
        return await self.__queue_controller.register.remote(consumer_name)

    async def finish(self, consumer_name: str | None = None):
        return await self.__queue_controller.finish.remote(consumer_name)
