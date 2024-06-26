from typing import Any
import ray
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.extra_api import ExtraApi


class RemoteCentralApi(DefaultCentralApi):
    remote_provider = ray

    def __init__(self, central_api_identifier: str):
        super().__init__(central_api_identifier)

    async def get_object_reference(self, obj_identifiers: list[str]):
        reference = await super().get_object_reference(obj_identifiers)  # type: ignore
        if reference is None:
            return None
        return ray.get(reference)

    async def get_object_reference_by_path(self, obj_path: str):
        reference = await super().get_object_reference_by_path(obj_path)  # type: ignore
        if reference is None:
            return None
        return ray.get(reference)

    async def put_remote_object_reference(
        self, obj_identifiers: list[str], reference: Any
    ):
        new_reference = ray.put(reference)
        return await super().put_remote_object_reference(obj_identifiers, new_reference)  # type: ignore

    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any):
        new_reference = ray.put(reference)
        return await super().put_remote_object_reference_by_path(
            obj_path, new_reference
        )
    
    async def list_objects(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None):
        result = await super().list_objects(prefix, suffix, matches)
        return [(x[0], ray.get(x[1])) for x in result]

    async def execute(self, command: Command, *args, **kwargs):
        return await super().execute(command, *args, **kwargs)
    
    async def generate_reference(self, data: Any):
        reference = ray.put(data)
        return reference
    
    async def get_data_from_reference(self, reference: Any):
        return ray.get(reference)
    
    async def put_extra_api(self, api: ExtraApi):
        return await super().put_extra_api(api)
