import asyncio
from itertools import chain
import os
from typing import Any, Callable, Generic, List, Tuple, TypeVar
from turbo_c2 import central_api
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.extra_api.command.crud_command import (
    CreateCommand,
    CrudCommand,
    DeleteCommand,
    GetCommand,
    UpdateCommand,
)
from turbo_c2.helpers.iterable_helpers import is_iterable
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")


class CrudResourceApi(Generic[Definition, Resource], NeedsCentralApi):
    def __init__(
        self,
        crud_command: CrudCommand,
        creators_keys: list[str],
        resource_id_is_path=False,
        exclude_commands: list[str] | None = None,
    ) -> None:
        self.__command = crud_command
        self.__creators_keys = creators_keys
        self.__logger = TurboLogger(f"Api({self.complete_path})")
        self.__resource_id_is_path = resource_id_is_path
        self.__exclude_commands = set(exclude_commands or [])
        self.__lock = asyncio.Lock()
        super().__init__()

    @property
    def complete_path(self):
        return [self.__command.api_identifier, *self.__command.api_path.split("/")]

    async def get_creator(self, creator_identifier: str):
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

            for x in await self.central_api.list_objects(
                prefix=os.path.join("/".join(self.complete_path), *fixed_prefix),
                suffix=suffix,
                # FIXME: don't search prefix repeated
                matches=matches,
            ):
                # If index path and not filter by prefix
                if len(x[0]) > len(self.complete_path) + 1 and not prefix:
                    continue

                result.append(x[1])

            return result

        fixed_resource_id = (
            [resource_id] if not self.__resource_id_is_path else resource_id.split("/")
        )

        return await self.central_api.get_object_reference(
            [*self.complete_path, *fixed_resource_id]
        )

    async def set(
        self,
        name: str,
        resource: Resource,
        fail_if_exists: bool | None = None,
        indexes: list[str] | None = None,
    ) -> None:
        resource_id = [name] if not self.__resource_id_is_path else name.split("/")

        if fail_if_exists:
            exists = await self.__get(name)

            if exists:
                raise ValueError(f"Resource {name} already exists")

        for index in indexes or []:
            value = getattr(resource, index, None)
            if value:
                if is_iterable(value):
                    for v in value:
                        await self.central_api.put_remote_object_reference(
                            [*self.complete_path, index, str(v), *resource_id], resource
                        )
                else:
                    await self.central_api.put_remote_object_reference(
                        [*self.complete_path, index, str(value), *resource_id], resource
                    )

        return await self.central_api.put_remote_object_reference(
            [*self.complete_path, *resource_id], resource
        )

    async def create(self, command: CreateCommand[Definition, Resource]) -> Resource:
        if not command.creator_id:
            creator_list = await self.list_creator_keys()
            if not creator_list:
                raise ValueError(
                    f"No creator found for create {command} on {self.__creators_keys}"
                )

            creator_id = creator_list[0]  # type: ignore

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
                    command.resource_id,
                    resource,
                    command.fail_if_exists,
                    indexes=command.indexes,
                )

        return resource

    async def update(self, command: UpdateCommand) -> None:
        async with self.__lock:
            exists = await self.__get(command.resource_id)

            if exists:
                await self.set(command.resource_id, command.resource)
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

    async def delete(self, command: DeleteCommand) -> None:
        raise NotImplementedError("Delete is not implemented yet")

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
