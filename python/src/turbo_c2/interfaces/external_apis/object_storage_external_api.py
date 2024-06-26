import abc
from typing import Hashable


class ObjectStorageExternalApi(abc.ABC):

    @abc.abstractmethod
    async def get_object_reference(
        self, obj_identifiers: list[Hashable]
    ) -> bytes | None:
        pass

    @abc.abstractmethod
    async def put_remote_object_reference(
        self, obj_identifiers: list[str], reference: bytes
    ):
        pass

    @abc.abstractmethod
    async def delete_item(self, obj_identifiers: list[Hashable]):
        pass

    @abc.abstractmethod
    async def list_objects(
        self,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ) -> list[tuple[list[str], bytes]]:
        pass
