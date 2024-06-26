from turbo_c2.decorators.queue import queue
from turbo_c2.domain.gui.layout_element_command import LayoutElementCommand
from turbo_c2.turbo_events.commands.event_store_controller_definition import (
    EventStoreControllerDefinition,
)
from turbo_c2.turbo_events.commands.event_store_creator_definition import (
    EventStoreCreatorDefinition,
)
from turbo_c2.turbo_events.commands.event_store_crud import EventStoreCrud
from turbo_c2.turbo_events.commands.event_store_type_definition import (
    EventStoreTypeDefinition,
)
from turbo_c2.turbo_events.commands.get_handler_layout_elements_command import GetHandlerLayoutElementsCommand
from turbo_c2.turbo_events.commands.handler_store_controller_definition import HandlerStoreControllerDefinition
from turbo_c2.turbo_events.commands.handler_store_creator_definition import HandlerStoreCreatorDefinition
from turbo_c2.turbo_events.commands.handler_store_crud import HandlerStoreCrud
from turbo_c2.turbo_events.commands.handler_store_type_definition import HandlerStoreTypeDefinition
from turbo_c2.turbo_events.event_based_boolean_scheduler_api import (
    EventBasedBooleanSchedulerApi,
)
from turbo_c2.turbo_events.event_based_boolean_scheduler_config import (
    EventBasedBooleanSchedulerConfig,
)
from turbo_c2.turbo_events.event_based_boolean_scheduler_globals import (
    EventBasedBooleanSchedulerGlobals,
)
from turbo_c2.turbo_events.event_based_rules_consumer import (
    EventBasedRulesConsumerJobFactory,
)
from turbo_c2.turbo_events.event_based_rules_executor import EventBasedRulesExecutorJobFactory
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.extra_api.command.gui.layout_element_command_crud import LayoutElementCommandCrud
from turbo_c2.scheduler.lazy_definable import LazyDefinable
from turbo_c2.scheduler.lazy_scheduler_parameters import LazySchedulerParameters
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.globals.scheduler_globals import SchedulerDefinitions


def get_event_queue_definition(name: str):
    @queue(for_types=[Event])
    def global_event_queue():
        return QueueDefinition(
            name, meta={"created_by": "default_scheduler"}
        )

    return global_event_queue


class EventBasedBooleanScheduler(LazyDefinable):
    def __init__(self, config: EventBasedBooleanSchedulerConfig | None = None) -> None:
        super().__init__("event_based_boolean_scheduler")
        self.config = config or EventBasedBooleanSchedulerGlobals.config
        self.__queue_name = self.config.default_queue_name
        self.__queue_meta = self.config.default_queue_meta
        self.__handlers = None
        self.__consumer_queues = None
        self.__event_store = None
        self.__executor_queue = None

    @property
    def queue_name(self):
        return self.__queue_name

    @property
    def event_store(self):
        if not self.__event_store:
            self.__event_store = (
                EventBasedBooleanSchedulerGlobals.default_event_store_creator()(
                    self.__handlers
                )
            )
        return self.__event_store

    def get_queues(self):
        self.__handlers = EventBasedBooleanSchedulerGlobals.get_handlers()
        handlers_queues = [
            QueueDefinition(queue) for x in self.__handlers for queue in x.queues
        ]
        queues = EventBasedBooleanSchedulerGlobals.get_queues()
        self.__consumer_queues = [get_event_queue_definition(self.__queue_name)]
        self.__executor_queue = QueueDefinition("turbo_events_executor_queue")

        return queues + self.__consumer_queues + handlers_queues + [self.__executor_queue]

    def get_remote_objects(self):
        return {}

    async def setup(
        self, scheduler_parameters: LazySchedulerParameters, *args, **kwargs
    ):
        for handler in self.__handlers:
            await handler.evaluate_queues(scheduler_parameters.queues)

        api = EventBasedBooleanSchedulerApi()
        api.add_central_api(scheduler_parameters.central_api)

        await scheduler_parameters.central_api.put_extra_api(api)

        (
            event_store_creator_type,
            name,
        ) = EventBasedBooleanSchedulerGlobals.default_event_store_creator()

        event_store_creator = event_store_creator_type()
        event_store_creator.add_central_api(scheduler_parameters.central_api)

        (
            handler_store_creator_type,
            name,
        ) = EventBasedBooleanSchedulerGlobals.default_handler_store_creator()

        handler_store_creator = handler_store_creator_type()
        handler_store_creator.add_central_api(scheduler_parameters.central_api)

        await scheduler_parameters.central_api.execute(
            EventStoreCreatorDefinition.set(
                event_store_creator,
                name,
            )
        )

        await scheduler_parameters.central_api.execute(
            HandlerStoreCreatorDefinition.set(
                handler_store_creator,
                name,
            )
        )

        (
            event_store_controller,
            name,
        ) = EventBasedBooleanSchedulerGlobals.default_event_store_controller()
        await scheduler_parameters.central_api.execute(
            EventStoreControllerDefinition.set(
                event_store_controller,
                name,
            )
        )

        (
            handler_store_controller,
            name,
        ) = EventBasedBooleanSchedulerGlobals.default_handler_store_controller()
        await scheduler_parameters.central_api.execute(
            HandlerStoreControllerDefinition.set(
                handler_store_controller,
                name,
            )
        )

        event_store_type, name = EventBasedBooleanSchedulerGlobals.default_event_store()
        await scheduler_parameters.central_api.execute(
            EventStoreTypeDefinition.set(
                event_store_type,
                name,
            )
        )

        handler_store_type, name = EventBasedBooleanSchedulerGlobals.default_handler_store()
        await scheduler_parameters.central_api.execute(
            HandlerStoreTypeDefinition.set(
                handler_store_type,
                name,
            )
        )

        event_store = await scheduler_parameters.central_api.execute(
            EventStoreCrud.create(
                definition=None,
                resource_id="default_event_store",
            )
        )

        handler_store = await scheduler_parameters.central_api.execute(
            HandlerStoreCrud.create(
                definition=EventBasedBooleanSchedulerGlobals.get_handlers(),
                resource_id="default_handler_store",
            )
        )

        EventBasedRulesConsumerJobFactory(
            event_store, self.__consumer_queues, self.__executor_queue
        ).get_job_constructor(**EventBasedBooleanSchedulerGlobals.consumer_settings)

        EventBasedRulesExecutorJobFactory(
            event_store, handler_store, [self.__executor_queue]
        ).get_job_constructor(**EventBasedBooleanSchedulerGlobals.executor_settings)

        await scheduler_parameters.central_api.execute(
            LayoutElementCommandCrud.create(
                resource_id="get_handler_layout_element",
                definition=LayoutElementCommand(
                    lazy_command=GetHandlerLayoutElementsCommand
                )
            )
        )

        return SchedulerDefinitions([], [])
