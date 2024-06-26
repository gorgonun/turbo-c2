import functools
from typing import Any
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.object_storage.json_resource import JsonResource
from turbo_c2.extra_api.command.object_storage.object_resource import ObjectResource
from turbo_c2.extra_api.command.object_storage.object_storage_enum import ObjectStorageEnum
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.resource_api import ResourceApi
from turbo_c2.interfaces.external_api import ExternalApi
from turbo_c2.interfaces.external_apis.object_storage_external_api import (
    ObjectStorageExternalApi,
)
from turbo_c2.jobs.needs_external_apis import NeedsExternalApis


class ObjectStorageExtraApi(DefaultExtraApiWithSubApis, NeedsExternalApis):
    def __init__(
        self,
        object_storage_api_name: str,
        json_object_storage_api_name: str,
        external_apis: dict[str, Any] | None = None,
        central_api: CentralApiApi | None = None,
    ) -> None:
        self.__object_resource_api = ResourceApi(ObjectResource)
        self.__json_resource_api = ResourceApi(JsonResource)
        self.__apis = [
            self.__object_resource_api,
            self.__json_resource_api,
        ]

        super().__init__(
            self.__apis,
            [
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            ObjectStorageEnum.API_ID.value,
            central_api=central_api,
        )

        NeedsExternalApis.__init__(
            self,
            external_apis_names=[object_storage_api_name, json_object_storage_api_name],
            external_apis=external_apis,
        )

        self.object_storage_api_name = object_storage_api_name
        self.json_object_storage_api_name = json_object_storage_api_name

        self.add_external_apis()

    @property
    def object_storage_api(self) -> ObjectStorageExternalApi:
        if not (
            object_storage_api := self.get_external_api(self.object_storage_api_name)
        ):
            raise ValueError(
                f"Object storage API {self.object_storage_api_name} not found"
            )

        return object_storage_api

    @property
    def json_object_storage_api(self) -> ObjectStorageExternalApi:
        if not (
            json_object_storage_api := self.get_external_api(
                self.json_object_storage_api_name
            )
        ):
            raise ValueError(
                f"JSON object storage API {self.json_object_storage_api_name} not found"
            )

        return json_object_storage_api

    def add_external_apis(self):
        if self.get_external_api(self.object_storage_api_name):
            self.__object_resource_api.add_external_api(self.object_storage_api)

        if self.get_external_api(self.json_object_storage_api_name):
            self.__json_resource_api.add_external_api(self.json_object_storage_api)

    def add_external_api(self, name: str, external_api: ExternalApi):
        super().add_external_api(name, external_api)
        self.add_external_apis()

    def __reduce__(self) -> str | tuple[Any, ...]:
        return (
            functools.partial(
                ObjectStorageExtraApi,
                object_storage_api_name=self.object_storage_api_name,
                json_object_storage_api_name=self.json_object_storage_api_name,
                external_apis=self.external_apis,
                central_api=self.central_api,
            ),
            tuple(),
        )
