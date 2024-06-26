from dataclasses import dataclass
from typing import ClassVar, Hashable

from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class GetQueueCommand(Command[Hashable, QueueApi]):
    queue_name: Hashable
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/get"
