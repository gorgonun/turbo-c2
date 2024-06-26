from dataclasses import dataclass
from turbo_c2.domain.gui.layout_definition import LayoutGroupDefinitionWithLayouts
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.interfaces.command import Command


@dataclass
class GetLayoutGroupDefinitionWithLayouts(Command[str, LayoutGroupDefinitionWithLayouts]):
    layout_group_id: str
    api_identifier = GuiEnum.API_ID.value
    api_path = "layout_group_definition/get_with_layouts"
