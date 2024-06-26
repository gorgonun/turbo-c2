from __future__ import annotations
from turbo_c2.turbo_events.operators.event_operators import Operation
from turbo_c2.turbo_events.operators.remote_store_event_expression import RemoteStoreEventExpression
from turbo_c2.turbo_events.events.event_reference import EventReference


def event_happened(event_reference: EventReference, inTimeWindowSeconds: int | None = None):
    return Operation(RemoteStoreEventExpression(event_reference, inTimeWindowSeconds))
