from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.interfaces.command import Command


@dataclass
class GetHandlersByEventTypeCommand(Command[tuple[str, str | None], None]):
    event_type: str
    controller_id: str | None = None
    api_identifier: ClassVar[str] = "event_based_boolean_scheduler"
    api_path: ClassVar[str] = "handler/get_by_event_type"
