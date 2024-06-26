from dataclasses import dataclass
from typing import ClassVar, Tuple, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class GetQueueApiCommand(Command[Tuple[str], Type[QueueApi]]):
    queue_api_id: str
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_api/get"
