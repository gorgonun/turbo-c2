import abc
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.operators.event_operators import Operation


class HandlerStore(abc.ABC):
    def __init__(self, identifier: str) -> None:
        self.__identifier = identifier

    @property
    def identifier(self):
        return self.__identifier

    @abc.abstractmethod
    async def register_handler(self, controller: Handler[Operation]) -> None:
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

    # FIXME: solve circular import with event_mapping
    @abc.abstractmethod
    def map_rules(
        self,
        handlers: list[Handler[Operation]],
        rules: dict = None,
    ) -> dict:
        pass

    @abc.abstractmethod
    async def get_handler_by_last_event(self, event: Event, session: str):
        pass

    @abc.abstractmethod
    async def get_handler_by_event_type(
        self, event_type: str
    ) -> list[Handler[Operation]]:
        pass
