from turbo_c2.domain.gui.layout_definition import LayoutGroupDefinition
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum


class LayoutGroupDefinitionCrud(CrudCommand[LayoutGroupDefinition, LayoutGroupDefinition]):
    api_identifier = GuiEnum.API_ID.value
    api_path = "layout_group_definition"
    indexes = ["group_path"]
