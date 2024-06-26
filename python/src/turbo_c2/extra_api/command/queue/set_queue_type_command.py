from dataclasses import dataclass
from typing import ClassVar, Tuple, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_definition import QueueDefinition


@dataclass
class SetQueueTypeCommand(Command[Tuple[Type[EBFQueue], Type[QueueDefinition], str | None], None]):
    queue_type: Type[EBFQueue]
    queue_definition_hash: Type[QueueDefinition]
    queue_definition_id: str | None = None
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_type/set"
