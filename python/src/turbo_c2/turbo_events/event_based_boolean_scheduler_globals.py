from typing import Tuple, Type
from turbo_c2.turbo_events.event_based_boolean_scheduler_config import DefaultEventBasedBooleanSchedulerConfig
from turbo_c2.turbo_events.event_store.event_controller import EventController
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.event_store.event_store_controller import EventStoreController
from turbo_c2.turbo_events.event_store.event_store_creator import EventStoreCreator
from turbo_c2.turbo_events.event_store.handler_store import HandlerStore
from turbo_c2.turbo_events.event_store.handler_store_controller import HandlerStoreController
from turbo_c2.turbo_events.event_store.handler_store_creator import HandlerStoreCreator
from turbo_c2.turbo_events.event_store.in_memory_event_store import InMemoryEventStore
from turbo_c2.turbo_events.event_store.in_memory_handler_store import InMemoryHandlerStore
from turbo_c2.turbo_events.event_store.remote_event_controller import RemoteEventController
from turbo_c2.turbo_events.event_store.remote_event_store_controller import RemoteEventStoreController
from turbo_c2.turbo_events.event_store.remote_event_store_creator import RemoteEventStoreCreator
from turbo_c2.turbo_events.event_store.remote_handler_store_controller import RemoteHandlerStoreController
from turbo_c2.turbo_events.event_store.remote_handler_store_creator import RemoteHandlerStoreCreator
from turbo_c2.turbo_events.handlers.handler_controller import HandlerController
from turbo_c2.turbo_events.handlers.local_dynamic_handler import LocalDynamicHandler
from turbo_c2.turbo_events.handlers.local_handler_controller import LocalHandlerController
from turbo_c2.queues.queue_definition import QueueDefinition


class EventBasedBooleanSchedulerGlobals():
    __handlers: list[HandlerController] = []
    __queues: list[QueueDefinition] = []
    __consumer_queues: list[QueueDefinition] = []
    event_store_mapping: dict[str, Tuple[Type[EventStore], str]] = {
        "remote": (InMemoryEventStore, "default"),
    }
    handler_store_mapping: dict[str, Tuple[Type[HandlerStore], str]] = {
        "remote": (InMemoryHandlerStore, "default"),
    }
    event_controller_mapping: dict[str, Type[EventController]] = {
        "remote": RemoteEventController,
    }
    event_controller_config = {
        "remote": {
            "event_store_actor_name": "event_store",
        }
    }
    event_store_controller_mapping: dict[str, Tuple[Type[EventStoreController], str]] = {
        "remote": (RemoteEventStoreController, "default"),
    }
    handler_store_controller_mapping: dict[str, Tuple[Type[HandlerStoreController], str]] = {
        "remote": (RemoteHandlerStoreController, "default"),
    }
    handler_controller_mapping: dict[str, Type[HandlerController]] = {
        "remote": LocalHandlerController
    }
    dynamic_handler_mapping: dict[str, Type[LocalDynamicHandler]] = {
        "remote": LocalDynamicHandler
    }
    event_store_creator_mapping: dict[str, Tuple[Type[EventStoreCreator], str]] = {
        "remote": (RemoteEventStoreCreator, "default")
    }
    handler_store_creator_mapping: dict[str, Tuple[Type[HandlerStoreCreator], str]] = {
        "remote": (RemoteHandlerStoreCreator, "default")
    }
    consumer_settings = {
        "replicas": 1,
    }
    executor_settings = {
        "replicas": 1,
    }
    config = DefaultEventBasedBooleanSchedulerConfig()

    @classmethod
    def default_event_store_creator(cls):
        return cls.event_store_creator_mapping[cls.config.mode]
    
    @classmethod
    def default_handler_store_creator(cls):
        return cls.handler_store_creator_mapping[cls.config.mode]

    @classmethod
    def default_event_controller(cls):
        return cls.event_controller_mapping[cls.config.mode](**cls.event_controller_config[cls.config.mode])
    
    @classmethod
    def default_event_store_controller(cls):
        return cls.event_store_controller_mapping[cls.config.mode]
    
    @classmethod
    def default_handler_store_controller(cls):
        return cls.handler_store_controller_mapping[cls.config.mode]
    
    @classmethod
    def default_event_store(cls):
        return cls.event_store_mapping[cls.config.mode]
    
    @classmethod
    def default_handler_store(cls):
        return cls.handler_store_mapping[cls.config.mode]
    
    @classmethod
    def default_handler_controller(cls):
        return cls.handler_controller_mapping[cls.config.mode]
    
    @classmethod
    def default_dynamic_handler(cls):
        return cls.dynamic_handler_mapping[cls.config.mode]

    @classmethod
    def add_handler(cls, handler: HandlerController):
        cls.__handlers.append(handler)

    @classmethod
    def add_handlers(cls, handlers: list[HandlerController]):
        cls.__handlers.extend(handlers)

    @classmethod
    def get_handlers(cls):
        return cls.__handlers
    
    @classmethod
    def add_queue(cls, queue: QueueDefinition):
        cls.__queues.append(queue)

    @classmethod
    def add_queues(cls, queues):
        cls.__queues.extend(queues)

    @classmethod
    def get_queues(cls):
        return cls.__queues
    
    @classmethod
    def add_consumer_queue(cls, queue: QueueDefinition):
        cls.__consumer_queues.append(queue)

    @classmethod
    def add_consumer_queues(cls, queues):
        cls.__consumer_queues.extend(queues)

    @classmethod
    def get_consumer_queues(cls):
        return cls.__consumer_queues
