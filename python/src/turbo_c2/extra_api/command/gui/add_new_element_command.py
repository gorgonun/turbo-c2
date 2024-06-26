from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.domain.gui.layout_definition import PositionDefinition
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class AddNewElementCommand(Command[Tuple[PositionDefinition, str, str, str], None]):
    element: PositionDefinition
    element_id: str
    layout_id: str
    element_type: str
    api_identifier: ClassVar[str] = GuiEnum.API_ID.value
    api_path: ClassVar[str] = "layout_definition/window_definition/add_new_element"
