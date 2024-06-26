import abc
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators.boolean import Operation


class HandlerStoreController(abc.ABC):
    @abc.abstractmethod
    async def register_handler(self, controller: Handler[Operation]) -> None:
        pass

    @abc.abstractmethod
    async def register_handlers(self, controllers: list[Handler[Operation]]) -> None:
        pass

    @abc.abstractmethod
    def unlock(self, session: str) -> None:
        pass

    @abc.abstractmethod
    async def set_lock_for_event(self, event: Event, time_mills: int | None) -> str:
        pass

    @abc.abstractmethod
    async def get_lock(self, event: Event) -> str:
        pass

    @abc.abstractmethod
    async def get_session_lock_for_event(self, event: Event) -> str | None:
        pass

    @abc.abstractmethod
    async def is_event_locked(self, event: Event, session_mapping: dict) -> bool:
        pass

    @abc.abstractmethod
    async def on_execution(
        self,
        evaluation_result: bool,
        controller: Handler[Operation],
        session: str,
    ) -> None:
        pass

    @abc.abstractmethod
    async def get_handler_by_last_event(self, event: Event, session: str | None):
        pass

    @abc.abstractmethod
    async def get_handler_by_last_events(self, events_with_session: list[tuple[str | None, Event]]):
        pass

    @abc.abstractmethod
    async def get_handler_by_event_type(
        self, event_type: str
    ) -> list[Handler[Operation]]:
        pass
