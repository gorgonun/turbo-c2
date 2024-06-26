from typing import Generic, TypeVar
from turbo_c2.extra_api.command.crud_client_resource_command import (
    CreateCommand,
    CrudClientResourceCommand,
    DeleteCommand,
    GetCommand,
    UpdateCommand,
)
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.helpers.iterable_helpers import is_iterable


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")
Api = TypeVar("Api")


class CrudClientResourceApi(Generic[Api, Definition, Resource], CrudResourceApi[Definition, Resource]):
    def __init__(self, crud_command: CrudClientResourceCommand, creators_keys: list[str], apis_keys: list[str], exclude_commands: list[str] | None = None) -> None:
        self.__apis_keys = apis_keys
        super().__init__(crud_command, creators_keys, exclude_commands=exclude_commands)

    async def __get_api(self, api_identifier: str) -> Api | None:
        return await self.central_api.get_object_reference(
            [*self.__apis_keys, api_identifier]
        )
    
    async def __list_apis(self) -> list[Api]:
        return [
            x[1]
            for x in await self.central_api.list_objects(
                prefix="/".join(self.__apis_keys)
            )
        ]
    
    async def __get_default_api(self) -> Api:
        return (await self.__list_apis())[0]

    async def create(self, command: CreateCommand[Definition, Resource]) -> Resource:
        resource = await super().create(command)

        if command.resource_client_id:
            api = await self.__get_api(command.resource_client_id)
        else:
            api = await self.__get_default_api()

        return api(resource)
    
    async def update(self, command: UpdateCommand[Resource]) -> None:
        return await super().update(command)

    async def get(self, command: GetCommand) -> Api | None:
        resource = await super().get(command)

        if not resource:
            return None

        if command.resource_client_id:
            api = await self.__get_api(command.resource_client_id)
        else:
            api = await self.__get_default_api()

        if is_iterable(resource):
            return [api(x) for x in resource]

        return api(resource)
    
    async def delete(self, command: DeleteCommand) -> None:
        return await super().delete(command)
