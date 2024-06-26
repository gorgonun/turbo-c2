import os
from typing import Any, Hashable, TypeVar, cast
from turbo_c2.helpers.path_mapping import PathMapping
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.command import Command
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.extra_api import ExtraApi


T = TypeVar("T")
U = TypeVar("U")


class DefaultCentralApi(CentralApi):
    extra_apis_path = "__extra_apis"

    def __init__(self, api_identifier: str, object_references: PathMapping | None = None) -> None:
        self.__api_identifier = api_identifier
        self.__object_references = object_references or PathMapping()
        self.__logger = TurboLogger(f"CentralApi({api_identifier})")
        self.__extra_api_cache = {}

    async def generate_reference(self, data: Any):
        return data
    
    async def get_data_from_reference(self, reference: Any):
        return reference

    async def get_api_identifier(self):
        return self.__api_identifier

    async def get_object_reference(self, obj_identifiers: list[Hashable]):
        return self.__object_references.get_resource(obj_identifiers)

    async def get_object_reference_by_path(self, obj_path: str):
        return await self.get_object_reference(obj_path.split(os.path.sep))

    async def put_remote_object_reference(
        self, obj_identifiers: list[Hashable], reference: Any
    ):
        # remote_resource = ray.put(reference)
        self.__object_references.put_resource(obj_identifiers, reference)

    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any):
        return await self.put_remote_object_reference(
            obj_path.split(os.path.sep), reference
        )
    
    # FIXME: The others put object with data. Only this puts with reference
    async def put_remote_object_with_reference(self, obj_identifiers: list[Hashable], reference: Any):
        self.__object_references.put_resource(obj_identifiers, reference)

    async def delete_item(self, obj_identifiers: list[Hashable]):
        self.__object_references.delete_item(obj_identifiers)

    async def get_object_reference_only(self, obj_identifiers: list[Hashable]):
        return self.__object_references.get_resource(obj_identifiers)
    
    async def list_objects(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None):
        return self.__object_references.get_all_resources(prefix, suffix, matches)

    async def put_extra_api(self, api: ExtraApi):
        api_reference = await self.generate_reference(api)

        for complete_path in api.paths:
            self.__logger.debug("PUT", complete_path, id(api), api_reference, id(api_reference))

            if await self.get_object_reference([self.extra_apis_path, *list(complete_path)]):
                self.__logger.warning(
                    f"API {api.api_id}/{complete_path} already exists, overwriting"
                )

            await self.put_remote_object_with_reference(
                [self.extra_apis_path, *list(complete_path)], api_reference
            )
            self.__extra_api_cache[api_reference] = api
            await self.put_remote_object_with_reference(
                [self.extra_apis_path, api.api_id, "self"], api_reference
            )

    async def get_extra_api(self, api_identifier: Hashable):
        return await self.get_object_reference([self.extra_apis_path, api_identifier, "self"])

    async def execute(self, command: Command[T, U], *args, **kwargs) -> U:
        self.__logger.debug("EXECUTE", command.api_identifier, command.api_path)
        api_reference = await self.get_object_reference_only(
            [self.extra_apis_path, command.api_identifier, *command.api_path.split("/")]
        )
        if not api_reference:
            raise ValueError(f"API {command.api_identifier}/{command.api_path} does not exist")

        api = self.__extra_api_cache.get(api_reference) or await self.get_data_from_reference(api_reference)
        return await cast(U, api.execute(command, *args, **kwargs))
