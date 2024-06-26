from dataclasses import dataclass, field
from typing import Any
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.jobs.edge_representation import EdgeRepresentation

from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.jobs.target_representation import TargetRepresentation
from turbo_c2.mixin.has_id import HasId



@dataclass
class EdgeLayoutElement:
    representation: EdgeRepresentation
    target_representation: TargetRepresentation
    target: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayoutElement(HasId):
    representation: NodeRepresentation
    x: float | None = None
    y: float | None = None
    width: int | None = None
    height: int | None = None
    resource_name: str | None = None
    sources: list[EdgeLayoutElement] | None = None
    destinations: list[EdgeLayoutElement] | None = None
    layout_element_id: str = NameUtils.get_anonymous_name("LayoutElement")

    @property
    def resource_id(self) -> str:
        return self.layout_element_id
