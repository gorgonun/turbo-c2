from typing import Type
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.turbo_events.event_store.handler_store_creator import HandlerStoreCreator


class HandlerStoreCreatorDefinition(DefinitionCommand[str, Type[HandlerStoreCreator]]):
    api_identifier = "event_based_boolean_scheduler"
    api_path = "handler_store_creator"
