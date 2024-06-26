from dataclasses import dataclass
from typing import Any, ClassVar
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class GenerateLayoutDefinitionForGroupCommand(Command[str, dict[str, Any]]):
    group_path: str
    api_identifier: ClassVar[str] = GuiEnum.API_ID.value
    api_path: ClassVar[str] = "layout_definition/generate"
