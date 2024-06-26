from dataclasses import dataclass
from typing import ClassVar, Hashable

from turbo_c2.interfaces.command import Command
from turbo_c2.queues.queue_creator import QueueCreator


@dataclass
class GetQueueCreatorCommand(Command[Hashable, QueueCreator]):
    queue_creator_name: Hashable
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_creator/get"
