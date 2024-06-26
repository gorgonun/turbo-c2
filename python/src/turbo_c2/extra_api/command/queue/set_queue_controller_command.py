from dataclasses import dataclass
from typing import ClassVar, Tuple, Type

from turbo_c2.interfaces.command import Command
from turbo_c2.queues.queue_controller import QueueController


@dataclass
class SetQueueControllerCommand(Command[Tuple[Type[QueueController], str], None]):
    queue_controller: Type[QueueController]
    queue_controller_id: str
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_controller/set"
