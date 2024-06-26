from dataclasses import dataclass
from typing import ClassVar, Type
from turbo_c2.interfaces.command import Command
from turbo_c2.queues.ebf_queue import EBFQueue


@dataclass
class GetQueueTypesCommand(Command[None, list[Type[EBFQueue]]]):
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue_type/get_all"
