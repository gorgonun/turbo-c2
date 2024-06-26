import abc
import uuid
from typing import Any
from turbo_c2.turbo_events.event_store.handler_store_controller import HandlerStoreController
from turbo_c2.turbo_events.handlers.handler_controller import HandlerController
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class HandlerStoreCreator(abc.ABC, NeedsCentralApi):
    def __init__(self, identifier: str | None = None) -> None:
        self.__identifier = identifier or "QueueCreator_" + uuid.uuid4().hex[:8] # type: ignore
        super().__init__()

    @property
    def identifier(self):
        return self.__identifier

    @abc.abstractmethod
    async def create(self, handlers: list[HandlerController], meta: dict[str, Any] | None=None) -> HandlerStoreController:
        pass
