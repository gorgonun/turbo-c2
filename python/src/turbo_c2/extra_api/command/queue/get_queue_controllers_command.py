from dataclasses import dataclass
from typing import ClassVar, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.queues.queue_controller import QueueController


@dataclass
class GetQueueControllersCommand(Command[None, list[Type[QueueController]]]):
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_controller/get_all"
