from typing import ClassVar
from turbo_c2.domain.gui.layout_element import LayoutElement
from turbo_c2.domain.gui.layout_element_command import ElementCommand


class GetHandlerLayoutElementsCommand(ElementCommand[None, list[LayoutElement]]):
    api_identifier: ClassVar[str] = "event_based_boolean_scheduler"
    api_path: ClassVar[str] = "handler/get_layout_elements"
