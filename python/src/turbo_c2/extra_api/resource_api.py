import asyncio
from itertools import chain
import os
from typing import Any, Callable, Generic, List, Tuple, TypeVar
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.extra_api.command.crud_command import (
    CreateCommand,
    CrudCommand,
    DeleteCommand,
    GetCommand,
    UpdateCommand,
)
from turbo_c2.extra_api.resources.default_creator import DefaultCreator
from turbo_c2.helpers.iterable_helpers import is_iterable
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.external_api import ExternalApi
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.jobs.needs_external_api import NeedsExternalApi


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")
API = TypeVar("API", bound=ExternalApi)


class ResourceApi(Generic[Definition, Resource, API], NeedsExternalApi[API], NeedsCentralApi):
    def __init__(
        self,
        crud_command: CrudCommand[Definition, Resource],
        creators_keys: list[str] | None = None,
        resource_id_is_path=False,
        exclude_commands: list[str] | None = None,
        before_write: Callable[[Resource], Any] | None = None,
        after_read: Callable[[Any], Any] | None = None,
    ) -> None:
        self.__command = crud_command
        self.__creators_keys = creators_keys
        self.__logger = TurboLogger(f"Api({self.complete_path})")
        self.__resource_id_is_path = resource_id_is_path
        self.__exclude_commands = set(exclude_commands or [])
        self.__lock = asyncio.Lock()
        self.__creator = DefaultCreator() if not self.__creators_keys else None
        self.__before_write = before_write
        self.__after_read = after_read
        super().__init__()

    @property
    def complete_path(self):
        return [self.__command.api_identifier, *self.__command.api_path.split("/")]
    
    @property
    def external_api(self):
        return super().external_api or self.central_api

    async def get_creator(self, creator_identifier: str | None):
        if creator_identifier is None:
            return self.__creator

        return await self.central_api.get_object_reference(
            [*self.__creators_keys, creator_identifier]
        )

    async def list_creator_keys(self):
        creators = await self.central_api.list_objects("/".join(self.__creators_keys))
        return list(
            chain.from_iterable([x[0][len(self.__creators_keys) :] for x in creators])
        )

    async def __get(
        self,
        resource_id: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ) -> Resource | None:
        if resource_id is None:
            fixed_prefix = [prefix] if prefix else []
            result = []

            for x in await self.external_api.list_objects(
                prefix=os.path.join("/".join(self.complete_path), *fixed_prefix),
                suffix=suffix,
                matches=matches,
            ):
                if self.__after_read:
                    result.append(self.__after_read(x[1]))
                else:
                    result.append(x[1])

            return result

        fixed_resource_id = (
            [resource_id] if not self.__resource_id_is_path else resource_id.split("/")
        )

        result = await self.external_api.get_object_reference(
            [*self.complete_path, *fixed_resource_id]
        )

        if self.__after_read and result:
            return self.__after_read(result)
        
        return result

    async def set(
        self,
        name: str,
        resource: Resource,
        fail_if_exists: bool | None = None,
        indexes: list[str] | None = None,
    ) -> None:
        resource_id = [name] if not self.__resource_id_is_path else name.split("/")
        if self.__before_write:
            resource = self.__before_write(resource)

        if fail_if_exists:
            exists = await self.__get(name)

            if exists:
                raise ValueError(f"Resource {name} already exists")

        for index in indexes or []:
            # Pydantic
            if isinstance(resource, dict):
                value = resource.get(index)
            else:
                value = getattr(resource, index, None)

            if value:
                if is_iterable(value):
                    for v in value:
                        await self.external_api.put_remote_object_reference(
                            [*self.complete_path, index, str(v), *resource_id], resource
                        )
                else:
                    await self.external_api.put_remote_object_reference(
                        [*self.complete_path, index, str(value), *resource_id], resource
                    )

        # FIXME: Missing id field name to insert together with the resource
        return await self.external_api.put_remote_object_reference(
            [*self.complete_path, *resource_id], resource
        )

    async def create(self, command: CreateCommand[Definition, Resource]) -> Resource:
        if not command.creator_id and self.__creators_keys:
            creator_list = await self.list_creator_keys()
            if not creator_list:
                raise ValueError(
                    f"No creator found for create {command} on {self.__creators_keys}"
                )

            creator_id = creator_list[0]  # type: ignore

        elif not command.creator_id:
            creator_id = None

        async with self.__lock:
            exists = await self.__get(command.resource_id)

            if exists:
                if command.fail_if_exists:
                    raise ValueError(f"Resource {command.resource_id} already exists")
                return exists

            creator = await self.get_creator(command.creator_id or creator_id)

            if not creator:
                raise ValueError(
                    f"Creator {command.creator_id or creator_id} from command {command} does not exist"
                )

            resource = await creator.create(command.definition, meta={"created_by": "/".join(self.complete_path)})  # type: ignore

            if is_iterable(resource):
                for r in resource:
                    await self.set(
                        command.resource_id,
                        r,
                        command.fail_if_exists,
                        indexes=command.indexes,
                    )
            else:
                await self.set(
                    name=command.resource_id,
                    resource=resource,
                    fail_if_exists=command.fail_if_exists,
                    indexes=command.indexes,
                )

        return resource

    async def update(self, command: UpdateCommand) -> None:
        async with self.__lock:
            exists = await self.__get(command.resource_id)

            if exists:
                await self.set(command.resource_id, command.resource, indexes=command.indexes)
            else:
                raise ValueError(f"Resource {command.resource_id} does not exist")

    async def get(self, command: GetCommand) -> Resource | None:
        self.__logger.debug("Getting resource", command.resource_id)

        return await self.__get(
            resource_id=command.resource_id,
            prefix=command.prefix,
            suffix=command.suffix,
            matches=command.matches,
        )

    # FIXME: It needs to delete from partition too
    async def delete(self, command: DeleteCommand) -> None:
        fixed_resource_id = (
            [command.resource_id] if not self.__resource_id_is_path else command.resource_id.split("/")
        )

        return await self.external_api.delete_item(
            [*self.complete_path, *fixed_resource_id],
        )

    def get_command_structure(
        self,
    ) -> List[Tuple[CommandPath, Callable[..., Any]] | None]:
        return list(
            filter(
                None,
                [
                    (
                        (self.__command.create_command_path(), self.create)
                        if "create" not in self.__exclude_commands
                        else None
                    ),
                    (
                        (self.__command.get_command_path(), self.get)
                        if "get" not in self.__exclude_commands
                        else None
                    ),
                    (
                        (self.__command.update_command_path(), self.update)
                        if "update" not in self.__exclude_commands
                        else None
                    ),
                    (
                        (self.__command.delete_command_path(), self.delete)
                        if "delete" not in self.__exclude_commands
                        else None
                    ),
                ],
            )
        )
