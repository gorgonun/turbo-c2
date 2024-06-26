from turbo_c2.domain.gui.elements_definition import ElementsDefinition
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum


class ElementsDefinitionResource(CrudCommand[ElementsDefinition, ElementsDefinition]):
    api_identifier = GuiEnum.API_ID.value
    api_path = "elements_definition_api/elements_definition"
