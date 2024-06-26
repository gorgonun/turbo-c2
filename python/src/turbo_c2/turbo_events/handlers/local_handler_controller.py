from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.handlers.handler_controller import HandlerController
from turbo_c2.turbo_events.handlers.local_dynamic_handler import LocalDynamicHandler
from turbo_c2.turbo_events.events.event import Event


class LocalHandlerController(HandlerController[LocalDynamicHandler]):
    def __init__(self, handler: LocalDynamicHandler):
        super().__init__(handler)

    @property
    def queues(self):
        return self.handler.not_evaluated_queues
    
    @property
    def when_true(self):
        return self.handler.when_true
    
    @property
    def when_false(self):
        return self.handler.when_false
    
    async def get_name(self):
        return self.handler.name

    async def execute(self, last_event: Event, event_store: EventStore, cache: dict | None = None):
        return await self.handler.execute(last_event, event_store, cache)
    
    async def get_when_true(self):
        return self.handler.when_true
    
    async def get_when_false(self):
        return self.handler.when_false
