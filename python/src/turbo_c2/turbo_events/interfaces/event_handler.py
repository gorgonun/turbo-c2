import abc
from typing import Generic, TypeVar
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.handlers.handler_action import HandlerAction
from turbo_c2.turbo_events.domain.handler_properties import HandlerProperties
from turbo_c2.turbo_events.operators.boolean import Boolean


T = TypeVar("T", bound=Boolean)


class EventHandler(Generic[T], abc.ABC):
    @property
    @abc.abstractmethod
    def when(self) -> T:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str | None:
        pass

    @property
    @abc.abstractmethod
    def when_true(self) -> HandlerAction:
        pass

    @property
    @abc.abstractmethod
    def when_false(self) -> HandlerAction | None:
        pass

    @property
    @abc.abstractmethod
    def properties(self) -> HandlerProperties:
        pass
    
    @abc.abstractmethod
    async def execute(self, last_event: Event, event_store: EventStore) -> bool:
        pass

    @abc.abstractmethod
    async def execute_when_true(self, last_event: Event) -> None:
        pass

    @abc.abstractmethod
    async def execute_when_false(self, last_event: Event) -> None:
        pass
