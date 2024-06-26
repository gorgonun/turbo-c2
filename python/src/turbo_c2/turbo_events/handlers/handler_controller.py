from typing import Any, Generic, TypeVar
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.handlers.local_dynamic_handler import LocalDynamicHandler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


T = TypeVar("T", bound=LocalDynamicHandler)


class HandlerController(Generic[T]):
    def __init__(self, handler: T):
        self.__handler = handler

    @property
    def handler(self):
        return self.__handler
    
    @property
    def properties(self):
        return self.handler.properties
    
    async def get_name(self):
        pass

    async def execute(self, last_event: Event, event_store: Any, cache: dict[EventReference, Event] | None = None):
        pass

    async def get_when_true(self):
        pass
    
    async def get_when_false(self):
        pass

    async def evaluate_queues(self, queues: dict[QueueReference, QueueApi]):
        await self.__handler.evaluate_queues(queues)
