from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.interfaces.command import Command
from turbo_c2.queues.queue_creator import QueueCreator


@dataclass
class GetQueueCreatorsCommand(Command[None, QueueCreator]):
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_creator/get_all"
