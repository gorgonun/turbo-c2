from dataclasses import dataclass
from typing import ClassVar, Hashable, Tuple

from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.queues.queue_definition import QueueDefinition


@dataclass
class CreateQueueCommand(Command[Tuple[QueueDefinition, Hashable, bool], QueueApi]):
    queue_definition: QueueDefinition
    creator_identifier: Hashable | None = None
    fail_if_exists: bool = True
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/create"
