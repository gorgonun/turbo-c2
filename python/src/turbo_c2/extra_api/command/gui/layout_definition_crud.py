from turbo_c2.domain.gui.layout_definition import LayoutDefinition
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum


class LayoutDefinitionCrud(CrudCommand[LayoutDefinition, LayoutDefinition]):
    api_identifier = GuiEnum.API_ID.value
    api_path = "layout_definition"
