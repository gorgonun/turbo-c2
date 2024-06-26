from dataclasses import dataclass
from turbo_c2.domain.gui.layout_definition import PositionDefinition


@dataclass
class ElementsDefinition:
    resource_id: str
    resource_position: PositionDefinition
