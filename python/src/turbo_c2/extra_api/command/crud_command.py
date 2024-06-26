import os
from dataclasses import dataclass
from typing import Generic, Hashable, Tuple, TypeVar
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.interfaces.dynamic_command import DynamicCommand


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")


@dataclass
class CreateCommand(
    DynamicCommand[Tuple[Definition, Hashable, Hashable | None, bool], Resource]
):
    definition: Definition
    resource_id: Hashable
    creator_id: Hashable | None = None
    fail_if_exists: bool = True
    indexes: list[str] | None = None
    api_identifier: str
    api_path: str


@dataclass
class GetCommand(DynamicCommand[str | None, Resource]):
    resource_id: str | None
    prefix: str | None = None
    suffix: str | None = None
    matches: str | None = None
    api_identifier: str
    api_path: str


@dataclass
class UpdateCommand(DynamicCommand[Tuple[Resource, str], None]):
    resource: Resource
    resource_id: str
    indexes: list[str] | None = None
    api_identifier: str
    api_path: str


@dataclass
class DeleteCommand(DynamicCommand[str, None]):
    resource_id: str
    api_identifier: str
    api_path: str
    indexes: list[str] | None = None


class CrudCommand(Generic[Definition, Resource]):
    api_identifier: str
    api_path: str
    indexes: list[str] | None = None

    @classmethod
    def create_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "create")

    @classmethod
    def get_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "get")

    @classmethod
    def update_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "update")

    @classmethod
    def delete_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "delete")

    @classmethod
    def create(
        cls,
        definition: Definition,
        resource_id: Hashable,
        creator_id: Hashable | None = None,
        fail_if_exists: bool = True,
    ) -> DynamicCommand[Definition, Resource]:
        return CreateCommand(
            definition=definition,
            creator_id=creator_id,
            resource_id=resource_id,
            fail_if_exists=fail_if_exists,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "create"),
            indexes=cls.indexes,
        )

    @classmethod
    def get(
        cls,
        resource_id: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ) -> DynamicCommand[str | None, Resource]:
        return GetCommand(
            resource_id=resource_id,
            prefix=prefix,
            suffix=suffix,
            matches=matches,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "get"),
        )

    @classmethod
    def update(
        cls, resource: Resource, resource_id: str
    ) -> DynamicCommand[Tuple[Resource, str], None]:
        return UpdateCommand(
            resource=resource,
            resource_id=resource_id,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "update"),
            indexes=cls.indexes,
        )

    @classmethod
    def delete(cls, resource_id: str) -> DynamicCommand[str, None]:
        return DeleteCommand(
            resource_id=resource_id,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "delete"),
            indexes=cls.indexes,
        )

    @classmethod
    def create_command(cls):
        return CreateCommand

    @classmethod
    def get_command(cls):
        return GetCommand

    @classmethod
    def update_command(cls):
        return UpdateCommand

    @classmethod
    def delete_command(cls):
        return DeleteCommand
