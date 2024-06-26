from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.api.domain.dto.job.position_definition_request import PositionDefinitionRequest
from turbo_c2.domain.gui.layout_definition import PositionDefinition
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class MoveElementsCommand(Command[Tuple[list[tuple[str, PositionDefinition]], str, str], None]):
    elements: dict[str, PositionDefinitionRequest]
    layout_id: str
    api_identifier: ClassVar[str] = GuiEnum.API_ID.value
    api_path: ClassVar[str] = "layout_definition/window_definition/move_elements"
