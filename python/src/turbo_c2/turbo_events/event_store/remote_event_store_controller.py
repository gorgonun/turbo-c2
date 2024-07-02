import time
from typing import TypeVar
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.event_store.event_store_controller import EventStoreController
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators.boolean import Operation


T = TypeVar("T", bound=EventStore)


# FIXME: this is an api, not controller
class RemoteEventStoreController(EventStoreController):
    def __init__(self, event_store: T):
        self.__event_store = event_store # type: ignore

    async def put_event(self, event: Event, acquire_lock: bool = True) -> str | None:
        return await self.__event_store.put_event.remote(event, acquire_lock)
    
    async def put_events(self, events: list[Event], acquire_lock: bool = True) -> list[str]:
        before_put_events = time.perf_counter()
        result = await self.__event_store.put_events.remote(events, acquire_lock)
        after_put_events = time.perf_counter()
        return result
    
    async def run(self):
        await self.__event_store.run.remote()

    async def graceful_shutdown(self):
        await self.__event_store.graceful_shutdown.remote()
    
    async def is_request_finished(self, req: str):
        return await self.__event_store.is_request_finished.remote(req)

    async def event_happened(self, event_reference: EventReference) -> bool:
        return await self.__event_store.event_happened.remote(event_reference)
    
    async def events_happened(self, event_references: list[EventReference]) -> dict[EventReference, bool]:
        return await self.__event_store.events_happened.remote(event_references)
