from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.domain.gui.layout_definition import WindowDefinition
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class GetWindowDefinitionForGroups(Command[Tuple[str, str | None], list[WindowDefinition | None]]):
    group_paths: list[str]
    layout_id: str | None = None
    api_identifier: ClassVar[str] = GuiEnum.API_ID.value
    api_path: ClassVar[str] = "layout_definition/window_definition/get_for_groups"
