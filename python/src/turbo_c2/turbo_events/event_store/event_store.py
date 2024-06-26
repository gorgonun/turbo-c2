import abc
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.operators.event_operators import Operation


# FIXME: Circular import. It is not type Handler, but HandlerController[Handler]. Remove event store from handler
class EventStore(abc.ABC):
    def __init__(self, identifier: str) -> None:
        self.__identifier = identifier

    @property
    def identifier(self):
        return self.__identifier

    @abc.abstractmethod
    def put_event(self, event: Event, acquire_lock: bool = True) -> str | None:
        pass

    @abc.abstractmethod
    def put_events(self, events: list[Event], acquire_lock: bool = True) -> list[str] | None:
        pass

    @abc.abstractmethod
    def run(self) -> None:
        pass

    @abc.abstractmethod
    def graceful_shutdown(self):
        pass

    @abc.abstractmethod
    def is_request_finished(self, req: str):
        pass

    @abc.abstractmethod
    def event_happened(self, event_reference: EventReference) -> bool:
        pass
