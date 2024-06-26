from typing import Any, Generic, Hashable, TypeVar
import uuid


T = TypeVar("T")


class QueueDefinition(Generic[T]):
    def __init__(self, name: str | None=None, meta: dict[str, Any] | None=None, aliases: list[Hashable] | None = None, can_handle_job_output: bool | None = None) -> None:
        self.__name = name or uuid.uuid4().hex
        self.__meta = meta or {}
        self.__aliases = aliases or []
        self.__can_handle_job_output = can_handle_job_output

    @property
    def meta(self):
        return self.__meta
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def aliases(self) -> list[Hashable]:
        return self.__aliases
    
    @aliases.setter
    def aliases(self, aliases: list[Hashable]):
        self.__aliases = aliases

    @property
    def can_handle_job_output(self) -> bool | None:
        return self.__can_handle_job_output

    def add_alias(self, *alias: Hashable):
        self.__aliases.extend(alias)

    def __hash__(self) -> int:
        return hash(self.__name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, QueueDefinition):
            return self.__name == o.name
        return False
