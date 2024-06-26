from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.turbo_events.events.event import Event
from turbo_c2.interfaces.command import Command


@dataclass
class DispatchEventsCommand(Command[Event, None]):
    events: list[Event]
    api_identifier: ClassVar[str] = "event_based_boolean_scheduler"
    api_path: ClassVar[str] = "event/dispatch_events"
