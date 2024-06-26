from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.interfaces.command import Command
from turbo_c2.turbo_events.handlers.handler_controller import HandlerController


@dataclass
class RegisterHandlerCommand(Command[HandlerController, None]):
    handler_controller: HandlerController
    controller_id: str | None = None
    api_identifier: ClassVar[str] = "event_based_boolean_scheduler"
    api_path: ClassVar[str] = "handler/register_handler"

    @property
    def args(self):
        return [self.handler_controller]
