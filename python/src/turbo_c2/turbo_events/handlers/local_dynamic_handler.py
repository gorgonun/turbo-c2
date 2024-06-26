import time
from typing import Any, Callable, TypeVar
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.handlers.handler_action import HandlerAction
from turbo_c2.turbo_events.interfaces.event_handler import EventHandler
from turbo_c2.turbo_events.domain.handler_properties import HandlerProperties
from turbo_c2.turbo_events.operators.event_expression import EventExpression
from turbo_c2.turbo_events.operators.event_operator_controller import (
    EventOperatorController,
)
from turbo_c2.helpers.iterable_helpers import is_iterable
from turbo_c2.mixin.needs_queue_evaluation import NeedsQueueEvaluation


T = TypeVar("T", bound=EventExpression)


class LocalDynamicHandler(EventHandler, NeedsQueueEvaluation):
    def __init__(
        self,
        when: T,
        when_true: HandlerAction,
        properties: HandlerProperties,
        args,
        when_false: HandlerAction | None = None,
        queue_mapping=None,
        name: str | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.__when = when
        self.__operator_controller = EventOperatorController(when)
        self.__when_true = when_true
        self.__when_false = when_false or HandlerAction(lambda _, __: None, [])
        self.__args = args or []
        self.__kwargs = kwargs or {}
        self.__name = name
        self.__properties = properties
        NeedsQueueEvaluation.__init__(
            self,
            [
                *(when_true.output_queues or []),
                *(when_false.output_queues if when_false else []),
            ],
            queues_reference_mapping=queue_mapping,
        )

    @property
    def when_true_outputs(self):
        return [self.queue_mapping[queue] for queue in self.__when_true.output_queues]

    @property
    def when_false_outputs(self):
        return [self.queue_mapping[queue] for queue in self.__when_false.output_queues]

    @property
    def when(self):
        return self.__when

    @property
    def name(self):
        return self.__name

    @property
    def when_true(self):
        return self.__when_true

    @property
    def when_false(self):
        return self.__when_false
    
    @property
    def kwargs(self):
        return self.__kwargs
    
    @property
    def properties(self):
        return self.__properties

    async def run(self, action: HandlerAction, *args, **kwargs) -> Any:
        result = action.run_function(*args, **kwargs)
        outputs = (
            self.when_true_outputs
            if action == self.__when_true
            else self.when_false_outputs
        )

        for output in outputs:
            if is_iterable(result):
                await output.put_iter(result)
            else:
                await output.put(result)

    async def execute(self, last_event: Event, event_store: EventStore, cache: dict[EventReference, bool] | None = None) -> bool:
        # before_start = time.perf_counter()
        # before_evaluate = time.perf_counter()
        result, all_events = await self.__operator_controller.evaluate(event_store, cache)
        # after_evaluate = time.perf_counter()
        # print(f"evaluate took {after_evaluate - before_evaluate} seconds")

        # before_execute = time.perf_counter()
        if result:
            await self.execute_when_true(last_event, all_events)
        else:
            await self.execute_when_false(last_event, all_events)

        # after_execute = time.perf_counter()
        # print(f"execute took {after_execute - before_execute} seconds")

        # after_start = time.perf_counter()
        # print(f"execute took {after_start - before_start} seconds")

        return result

    async def execute_when_true(self, last_event: Event, all_events: list[Event]) -> None:
        return await self.run(
            self.__when_true, last_event, all_events, *self.__args, **self.__kwargs
        )

    async def execute_when_false(self, last_event: Event, all_events: list[Event]) -> None:
        return await self.run(
            self.__when_false, last_event, all_events, *self.__args, **self.__kwargs
        )
    
    def get_user_kwargs(self, mapping: dict[str, Any], function: Callable[..., Any]) -> dict[str, Any]:
        return {key: mapping[key] for key in function.__code__.co_varnames if key in mapping}

    def __reduce__(self):
        return (
            LocalDynamicHandler.create,
            (
                self.when,
                self.__when_true,
                self.__properties,
                self.__args,
                self.__when_false,
                self.queue_mapping,
                self.__name,
                self.__kwargs,
            ),
        )

    def __repr__(self):
        return f"LocalDynamicHandler({self.when}, {self.when_true}, {self.__args}, {self.when_false}, {self.queue_mapping}, {self.__name}, {self.__kwargs})"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return (
            isinstance(other, LocalDynamicHandler)
            and self.when == other.when
            and self.when_true == other.when_true
            and self.when_false == other.when_false
            and self.queue_mapping == other.queue_mapping
            and self.name == other.name
            and self.kwargs == other.kwargs
        )

    @classmethod
    def create(
        cls,
        when: T,
        when_true: Callable[[list[Event]], None],
        properties: HandlerProperties,
        args,
        when_false: Callable[[list[Event]], None] | None = None,
        queue_mapping=None,
        name: str | None = None,
        kwargs=None,
    ):
        return cls(
            args=args,
            when=when,
            when_true=when_true,
            properties=properties,
            when_false=when_false,
            queue_mapping=queue_mapping,
            name=name,
            kwargs=kwargs,
        )
