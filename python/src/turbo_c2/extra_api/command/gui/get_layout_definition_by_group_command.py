from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.domain.gui.layout_definition import LayoutDefinition
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class GetLayoutDefinitionByGroup(Command[Tuple[str, str | None], LayoutDefinition | None]):
    group_path: str
    layout_id: str | None = None
    layout_group_id: str | None = None
    api_identifier: ClassVar[str] = GuiEnum.API_ID.value
    api_path: ClassVar[str] = "layout_definition/get_by_group"
