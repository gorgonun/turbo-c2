from typing import Any, Callable, Generic, List, Tuple, TypeVar
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.extra_api.command.crud_command import GetCommand
from turbo_c2.extra_api.command.definition_command import DefinitionCommand, ListCommand, SetCommand
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")


class DefinitionResourceApi(Generic[Definition, Resource], NeedsCentralApi):
    def __init__(self, definition_command: DefinitionCommand) -> None:
        self.__definition = definition_command
        self.__logger = TurboLogger(f"Api({self.complete_path})")
        super().__init__()

    @property
    def complete_path(self):
        return [self.__definition.api_identifier, *self.__definition.api_path.split("/")]

    async def __get(self, resource_id: str | None = None) -> Resource | None:
        if resource_id is None:
            get_all = [
                x[1]
                for x in await self.central_api.list_objects(
                    prefix="/".join(self.complete_path)
                )
            ]

            return get_all or []

        return await self.central_api.get_object_reference(
            [*self.complete_path, resource_id]
        )

    async def get(self, command: GetCommand) -> Resource | None:
        self.__logger.debug("Getting resource", command.resource_id)

        return await self.__get(command.resource_id)

    async def set(self, command: SetCommand) -> None:
        if command.fail_if_exists:
            exists = await self.__get(command.resource_id)

            if exists:
                raise ValueError(f"Resource {command.resource_id} already exists")

        if isinstance(command.resource, NeedsCentralApi):
            command.resource.add_central_api(self.central_api)

        return await self.central_api.put_remote_object_reference(
            [*self.complete_path, command.resource_id], command.resource
        )
    
    async def list_items(self, _: ListCommand) -> list[Resource]:
        return await self.__get(None)

    def get_command_structure(
        self,
    ) -> List[Tuple[CommandPath, Callable[..., Any]] | None]:
        return [
            (self.__definition.get_command_path(), self.get),
            (self.__definition.list_command_path(), self.list_items),
            (self.__definition.set_command_path(), self.set),
        ]
