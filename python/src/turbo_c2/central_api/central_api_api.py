from typing import Any, Hashable
import ray
from turbo_c2.central_api.remote_central_api import RemoteCentralApi
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.extra_api import ExtraApi


class CentralApiApi(CentralApi):
    remote_provider = ray

    def __init__(self, central_api_identifier: str):
        self.__central_api: RemoteCentralApi = self.remote_provider.remote(RemoteCentralApi).options(name=central_api_identifier, get_if_exists=True).remote(central_api_identifier)  # type: ignore

    async def get_api_identifier(self):
        return await self.__central_api.get_api_identifier.remote()  # type: ignore

    async def get_object_reference(self, obj_identifiers: list[str]):
        return await self.__central_api.get_object_reference.remote(obj_identifiers)  # type: ignore

    async def get_object_reference_by_path(self, obj_path: str):
        return await self.__central_api.get_object_reference_by_path.remote(obj_path)  # type: ignore

    async def put_remote_object_reference(
        self, obj_identifiers: list[str], reference: Any
    ):
        return await self.__central_api.put_remote_object_reference.remote(obj_identifiers, reference)  # type: ignore

    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any):
        return await self.__central_api.put_remote_object_reference_by_path.remote(
            obj_path, reference
        )

    async def delete_item(self, obj_identifiers: list[str]):
        return await self.__central_api.delete_item.remote(obj_identifiers)

    async def list_objects(
        self,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ):
        return await self.__central_api.list_objects.remote(prefix, suffix, matches)

    async def execute(self, command: Command, *args, **kwargs):
        return await self.__central_api.execute.remote(command, *args, **kwargs)

    async def generate_reference(self, data: Any):
        return await self.__central_api.generate_reference.remote(data)

    async def put_extra_api(self, api: ExtraApi):
        return await self.__central_api.put_extra_api.remote(api)

    async def get_extra_api(self, api_identifier: Hashable):
        return await self.__central_api.get_extra_api.remote(api_identifier)
