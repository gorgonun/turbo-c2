import abc
from typing import Any, Generic, Hashable, TypeVar


T = TypeVar("T")
U = TypeVar("U")


class ExternalApi(abc.ABC, Generic[T, U]):
    @property
    @abc.abstractmethod
    def api_identifier(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def deletion_base_path(self) -> str:
        pass

    @abc.abstractmethod
    async def get_api_identifier(self) -> str:
        pass

    @abc.abstractmethod
    async def get_object_reference(self, obj_identifiers: list[Hashable]) -> U:
        pass

    @abc.abstractmethod
    async def get_object_reference_by_path(self, obj_path: str) -> U:
        pass

    @abc.abstractmethod
    async def put_remote_object_reference(
        self, obj_identifiers: list[Hashable], reference: T
    ) -> None:
        pass

    @abc.abstractmethod
    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any) -> None:
        pass

    @abc.abstractmethod
    async def list_objects(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None) -> list[tuple[list[str], U]]:
        pass

    @abc.abstractmethod
    async def delete_item(self, obj_identifiers: list[Hashable]) -> None:
        pass
