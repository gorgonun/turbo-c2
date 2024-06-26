from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import EventBasedBooleanSchedulerGlobals
from turbo_c2.turbo_events.event_store.event_store_controller import EventStoreController
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators.boolean import Operation


class LocalEventStoreController(EventStoreController):
    def __init__(self):
        self.__event_store = EventBasedBooleanSchedulerGlobals.event_store_mapping[EventBasedBooleanSchedulerGlobals.config.profile]()

    async def register_handler(self, handler: Handler) -> None:
        return await self.__event_store.register_handler(handler)
    
    async def get_handler_by_last_event(self, event: Event, lock_time_mills: int | None = None) -> list[Handler]:
        return await self.__event_store.get_handler_by_last_event(event, lock_time_mills=lock_time_mills)
    
    async def get_handler_by_event_type(self, event_type: str) -> list[Handler[Operation]]:
        return await self.__event_store.get_handler_by_event_type(event_type)
    
    async def put_event(self, event: Event) -> None:
        return await self.__event_store.put_event(event)

    async def event_happened(self, event_reference: EventReference) -> bool:
        return await self.__event_store.event_happened(event_reference)
    
    async def unlock(self):
        return await self.__event_store.unlock()

    async def set_lock(self, lock: bool, time_mills: int | None):
        return await self.__event_store.set_lock(lock, time_mills)
