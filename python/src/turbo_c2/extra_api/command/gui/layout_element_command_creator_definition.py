from turbo_c2.domain.gui.layout_element_command import LayoutElementCommand
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum


class LayoutElementCommandCreatorDefinition(DefinitionCommand[LayoutElementCommand, LayoutElementCommand]):
    api_identifier = GuiEnum.API_ID.value
    api_path = "layout_element_command_creators/element"
