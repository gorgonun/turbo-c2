from __future__ import annotations
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.operators.references import HasReference
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.operators import boolean


class EventExpression(boolean.Boolean, HasReference):
    def __init__(self, event_reference: EventReference, in_time_window_seconds: int):
        HasReference.__init__(self, event_reference)
        self.in_time_window_seconds = in_time_window_seconds

    @property
    def events(self) -> list[EventReference]:
        return [self.reference]
    
    def __repr__(self) -> str:
        return f"EventHappened({self.reference.reference}, {self.in_time_window_seconds})"
    
    def __str__(self) -> str:
        return repr(self)
    
    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return repr(self) == repr(other)

    async def event_happened(self, event_reference: EventReference, event_store: EventStore):
        return await event_store.event_happened(event_reference)
