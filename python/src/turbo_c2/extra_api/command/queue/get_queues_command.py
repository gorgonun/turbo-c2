from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class GetQueuesCommand(Command[None, list[QueueApi]]):
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/get_all"
