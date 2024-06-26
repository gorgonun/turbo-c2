from dataclasses import dataclass
from typing import ClassVar, Tuple, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_definition import QueueDefinition


@dataclass
class GetQueueTypeCommand(Command[Tuple[str], Type[EBFQueue]]):
    queue_type_id: str | None = None
    queue_definition_hash: Type[QueueDefinition] | None = None
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_type/get"
