from dataclasses import dataclass
from typing import Any, ClassVar, Type

from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class GetQueuesByTypeCommand(Command[Type[Any]| Any, list[QueueApi]]):
    obj_or_type: Type[Any]| Any
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/get_by_type"
