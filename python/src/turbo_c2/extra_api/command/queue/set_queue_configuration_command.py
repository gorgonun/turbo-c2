from dataclasses import dataclass
from typing import Any, ClassVar, Tuple

from turbo_c2.interfaces.command import Command


@dataclass
class SetQueueConfigurationCommand(Command[Tuple[list[str], Any], None]):
    configuration_path: list[str]
    configuration_value: Any
    api_identifier: ClassVar[str] = "turbo"
    api_path: ClassVar[str] = "queue/configuration/set"
