from dataclasses import dataclass, field
from typing import Any, Generic, Type, TypeVar
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.interfaces.command import Command


T = TypeVar("T")
U = TypeVar("U")


@dataclass
class ElementCommand(Command[T, U]):
    group_path: str


@dataclass
class LayoutElementCommand(Generic[T, U]):
    lazy_command: Type[ElementCommand[T, U]]
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    element_resource_id: str = field(default_factory=lambda: NameUtils.get_anonymous_name("LayoutElementCommand"))

    @property
    def resource_id(self) -> str:
        return self.element_resource_id
