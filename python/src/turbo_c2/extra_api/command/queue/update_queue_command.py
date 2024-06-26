from dataclasses import dataclass
from typing import ClassVar, Hashable, Tuple

from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class UpdateQueueCommand(Command[Tuple[QueueApi, str, Hashable], None]):
    queue_api: QueueApi
    queue_name: str
    creator_identifier: Hashable | None = None
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/update"
