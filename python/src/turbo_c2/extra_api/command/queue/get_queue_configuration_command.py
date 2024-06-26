from dataclasses import dataclass
from typing import Any, ClassVar

from turbo_c2.interfaces.command import Command


@dataclass
class GetQueueConfigurationCommand(Command[list[str], Any]):
    configuration_path: list[str]
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/configuration/get"
