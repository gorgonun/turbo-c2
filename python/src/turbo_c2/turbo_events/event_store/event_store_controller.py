import abc
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators.boolean import Operation


class EventStoreController(abc.ABC):
    @abc.abstractmethod
    def put_event(self, event: Event, acquire_lock: bool = True) -> str | None:
        pass

    @abc.abstractmethod
    def put_events(self, events: list[Event], acquire_lock: bool = True) -> str:
        pass

    @abc.abstractmethod
    async def run(self) -> None:
        pass

    @abc.abstractmethod
    async def graceful_shutdown(self):
        pass

    @abc.abstractmethod
    async def is_request_finished(self, req: str):
        pass

    @abc.abstractmethod
    async def event_happened(self, event_reference: EventReference) -> bool:
        pass
    
    @abc.abstractmethod
    async def events_happened(self, event_references: list[EventReference]) -> dict[EventReference, bool]:
        pass
