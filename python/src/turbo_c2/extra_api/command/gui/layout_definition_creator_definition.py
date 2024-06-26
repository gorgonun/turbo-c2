from turbo_c2.domain.gui.layout_definition import WindowDefinition
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum


class LayoutDefinitionCreatorDefinition(DefinitionCommand[WindowDefinition, WindowDefinition]):
    api_identifier = GuiEnum.API_ID.value
    api_path = "layout_definition_creators"
