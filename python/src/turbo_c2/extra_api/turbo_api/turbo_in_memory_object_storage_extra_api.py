import functools
from typing import Any
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.in_memory_object_storage.in_memory_object_storage_enum import InMemoryObjectStorageEnum
from turbo_c2.extra_api.command.in_memory_object_storage.memory_resource import MemoryResource
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.resource_api import ResourceApi


class InMemoryObjectStorageExtraApi(DefaultExtraApiWithSubApis):
    def __init__(self, central_api: CentralApiApi | None = None) -> None:
        self.__apis = [ResourceApi(MemoryResource)]

        super().__init__(
            self.__apis,
            [
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            InMemoryObjectStorageEnum.API_ID.value,
            central_api=central_api
        )
    
    def __reduce__(self) -> str | tuple[Any, ...]:
        return functools.partial(InMemoryObjectStorageExtraApi, central_api=self.central_api), tuple()
