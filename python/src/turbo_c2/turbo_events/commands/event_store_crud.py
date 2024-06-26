from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.turbo_events.event_store.event_store import EventStore


class EventStoreCrud(CrudCommand[str, EventStore]):
    api_identifier = "event_based_boolean_scheduler"
    api_path = "event_store"
