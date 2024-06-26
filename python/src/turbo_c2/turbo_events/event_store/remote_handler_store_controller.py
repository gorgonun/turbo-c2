from typing import TypeVar
from turbo_c2.turbo_events.event_store.handler_store import HandlerStore
from turbo_c2.turbo_events.event_store.handler_store_controller import HandlerStoreController
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.operators.boolean import Operation


T = TypeVar("T", bound=HandlerStore)


# FIXME: this is an api, not controller
class RemoteHandlerStoreController(HandlerStoreController):
    def __init__(self, event_store: T):
        self.__event_store = event_store # type: ignore

    async def register_handler(self, controller: Handler[Operation]) -> None:
        return await self.__event_store.register_handler.remote(controller)
    
    async def register_handlers(self, controllers: list[Handler[Operation]]) -> None:
        return await self.__event_store.register_handlers.remote(controllers)

    async def unlock(self, session: str) -> None:
        return await self.__event_store.unlock.remote(session)

    async def set_lock_for_event(self, event: Event, time_mills: int | None) -> str:
        return await self.__event_store.set_lock_for_event.remote(event, time_mills)

    async def get_lock(self, event: Event) -> str:
        return await self.__event_store.get_lock.remote(event)

    async def get_session_lock_for_event(self, event: Event) -> str | None:
        return await self.__event_store.get_session_lock_for_event.remote(event)

    async def is_event_locked(self, event: Event, session_mapping: dict) -> bool:
        return await self.__event_store.is_event_locked.remote(event, session_mapping)

    async def on_execution(
        self,
        evaluation_result: bool,
        controller: Handler[Operation],
        session: str,
    ) -> None:
        return await self.__event_store.on_execution.remote(evaluation_result, controller, session)

    async def get_handler_by_last_event(self, event: Event, session: str | None):
        return await self.__event_store.get_handler_by_last_event.remote(event, session)
    
    async def get_handler_by_last_events(self, events_with_session: list[tuple[str | None, Event]]):
        return await self.__event_store.get_handler_by_last_events.remote(events_with_session)

    async def get_handler_by_event_type(
        self, event_type: str
    ) -> list[Handler[Operation]]:
        return await self.__event_store.get_handler_by_event_type.remote(event_type)

