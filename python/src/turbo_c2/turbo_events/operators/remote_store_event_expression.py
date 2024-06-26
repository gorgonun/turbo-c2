from __future__ import annotations
from turbo_c2.helpers.date_time import DateTime
from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import EventBasedBooleanSchedulerGlobals
from turbo_c2.turbo_events.operators.event_expression import EventExpression
from turbo_c2.turbo_events.events.event_reference import EventReference


class RemoteStoreEventExpression(EventExpression):
    __dt = DateTime()

    def __init__(self, event_reference: EventReference, inTimeWindowSeconds: int | None = None):
        super().__init__(event_reference, inTimeWindowSeconds)
        self.__event_controller = EventBasedBooleanSchedulerGlobals.default_event_controller()

    # def __event_happened(self, event_reference: EventReference):
    #     return (self.__dt.now() - self.__event_store.get_store().get_handler_by_last_event(event_reference).datetime).total_seconds <= inTimeWindowSeconds

    def event_happened(self, event_reference: EventReference):
        return self.__event_controller.event_happened(event_reference)
