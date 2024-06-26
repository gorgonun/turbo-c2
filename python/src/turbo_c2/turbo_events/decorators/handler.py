from typing import Callable
from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import (
    EventBasedBooleanSchedulerGlobals,
)
from turbo_c2.turbo_events.handlers.handler_action import HandlerAction
from turbo_c2.turbo_events.domain.handler_properties import HandlerProperties
from turbo_c2.globals.ebf_global import get_scheduler_globals

from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.operators.boolean import Boolean
from turbo_c2.queues.queue_definition import QueueDefinition


def when(
    predicate: Boolean,
    *args,
    when_true: HandlerAction | None = None,
    when_false: HandlerAction | None = None,
    outputs=None,
    handler_properties=None,
    **kwargs
):
    def wrapped(func: Callable[[Event], None]):
        if when_true is not None and outputs is not None:
            raise ValueError(
                "You can't define when_true and outputs at the same time. Set output queues on action."
            )

        properties = handler_properties or HandlerProperties()
        queues = [QueueDefinition(x) for x in outputs or []]
        handler = EventBasedBooleanSchedulerGlobals.default_handler_controller()(
            EventBasedBooleanSchedulerGlobals.default_dynamic_handler()(
                args=args,
                kwargs=kwargs,
                when=predicate,
                when_true=when_true or HandlerAction(run_function=func, output_queues=[x.name for x in queues]),
                when_false=when_false,
                properties=properties
            )
        )
        if not get_scheduler_globals().is_remote_only():
            EventBasedBooleanSchedulerGlobals.add_handler(handler)
            EventBasedBooleanSchedulerGlobals.add_queues(queues)

        return handler

    return wrapped
