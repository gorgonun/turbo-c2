from dataclasses import dataclass
from typing import ClassVar, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class GetQueueApisCommand(Command[None, list[Type[QueueApi]]]):
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_api/get_all"
