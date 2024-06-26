import abc
from typing import Any, Hashable, TypeVar
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.extra_api import ExtraApi


T = TypeVar("T")
U = TypeVar("U")


class CentralApi(abc.ABC):
    @abc.abstractmethod
    async def get_api_identifier(self):
        pass

    @abc.abstractmethod
    async def get_object_reference(self, obj_identifiers: list[Hashable]) -> Any:
        pass

    @abc.abstractmethod
    async def get_object_reference_by_path(self, obj_path: str):
        pass

    @abc.abstractmethod
    async def put_remote_object_reference(
        self, obj_identifiers: list[Hashable], reference: Any
    ):
        pass

    @abc.abstractmethod
    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any):
        pass

    @abc.abstractmethod
    async def delete_item(self, obj_identifiers: list[Hashable]):
        pass

    @abc.abstractmethod
    async def list_objects(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None) -> list[tuple[list[str], Any]]:
        pass

    @abc.abstractmethod
    async def put_extra_api(self, api: ExtraApi):
        pass

    @abc.abstractmethod
    async def get_extra_api(self, api_identifier: Hashable):
        pass

    @abc.abstractmethod
    async def execute(self, command: Command[T, U], *args, **kwargs) -> U:
        pass
