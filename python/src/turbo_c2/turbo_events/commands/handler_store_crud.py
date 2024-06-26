from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.turbo_events.event_store.handler_store import HandlerStore


class HandlerStoreCrud(CrudCommand[str, HandlerStore]):
    api_identifier = "event_based_boolean_scheduler"
    api_path = "handler_store"
