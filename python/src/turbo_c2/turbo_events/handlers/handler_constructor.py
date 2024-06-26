from typing import Any, Callable, Generic, TypeVar
from turbo_c2.globals.ebf_global import DefaultSchedulerGlobals
from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import (
    EventBasedBooleanSchedulerGlobals,
)
from turbo_c2.turbo_events.handlers.remote_dynamic_handler import (
    RemoteDynamicHandler,
)
from turbo_c2.turbo_events.operators.boolean import Boolean

from turbo_c2.turbo_events.events.event import Event
from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T", bound=Boolean)


# FIXME: implement this
class HandlerConstructor(Generic[T]):
    def __init__(
        self,
        when: T,
        *args,
        when_true: Callable[[Event], None] | None = None,
        when_false: Callable[[Event], None] | None = None,
        input_controller=None,
        outputs=None,
        **kwargs
    ):
        self.when = when
        self.args = args
        self.when_true = when_true
        self.when_false = when_false
        self.input_controller = input_controller
        self.outputs = outputs
        self.kwargs = kwargs

    def __call__(self, func: Callable[[Event], None]) -> Any:
        queues = [QueueDefinition(x) for x in self.outputs or []]
        input_controller_queue = QueueDefinition(self.input_controller)
        handler_controller = (
            EventBasedBooleanSchedulerGlobals.default_handler_controller()(
                RemoteDynamicHandler(
                    *self.args,
                    **{
                        **self.kwargs,
                        "when": self.when,
                        "when_true": self.when_true or func,
                        "when_false": self.when_false,
                        "outputs": queues,
                        "input_controller": self.input_controller,
                    }
                )
            )
        )
        EventBasedBooleanSchedulerGlobals.add_handler(handler_controller)
        DefaultSchedulerGlobals.add_queues([*queues, input_controller_queue])
