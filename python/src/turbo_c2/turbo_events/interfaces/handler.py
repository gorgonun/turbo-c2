import abc
from typing import Any, Generic, TypeVar
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.domain.handler_properties import HandlerProperties
from turbo_c2.turbo_events.operators.event_operators import Operation


T = TypeVar("T", bound=Operation)


class Handler(Generic[T], abc.ABC):
    @property
    @abc.abstractmethod
    def when(self):
        pass

    @property
    @abc.abstractmethod
    def properties(self) -> HandlerProperties:
        pass

    @abc.abstractmethod
    async def when_true(self, last_event: Event) -> None:
        pass

    @abc.abstractmethod
    async def when_false(self, last_event: Event) -> None:
        pass

    @abc.abstractmethod
    async def execute(self, last_event: Event, event_store: Any) -> bool:
        pass
