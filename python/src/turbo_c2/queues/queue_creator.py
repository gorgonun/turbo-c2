import abc
from typing import Any
import uuid
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.queues.queue_definition import QueueDefinition


class QueueCreator(abc.ABC, NeedsCentralApi):
    def __init__(self, identifier: str | None = None) -> None:
        self.__identifier = identifier or "QueueCreator_" + uuid.uuid4().hex[:8] # type: ignore
        self.__logger = TurboLogger(self.__identifier)
        super().__init__()

    @property
    def identifier(self):
        return self.__identifier
    
    @property
    def logger(self):
        return self.__logger

    @abc.abstractmethod
    async def create(self, definition: QueueDefinition, meta: dict[str, Any] | None=None) -> QueueApi:
        pass
