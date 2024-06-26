from typing import Type
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.turbo_events.event_store.event_store_controller import EventStoreController


class EventStoreControllerDefinition(DefinitionCommand[str, Type[EventStoreController]]):
    api_identifier = "event_based_boolean_scheduler"
    api_path = "event_store_controller"
