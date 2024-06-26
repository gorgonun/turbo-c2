import abc
import uuid
from typing import Any
from turbo_c2.turbo_events.event_store.event_store_controller import EventStoreController
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class EventStoreCreator(abc.ABC, NeedsCentralApi):
    def __init__(self, identifier: str | None = None) -> None:
        self.__identifier = identifier or "QueueCreator_" + uuid.uuid4().hex[:8] # type: ignore
        super().__init__()

    @property
    def identifier(self):
        return self.__identifier

    @abc.abstractmethod
    async def create(self, definition, meta: dict[str, Any] | None=None) -> EventStoreController:
        pass
