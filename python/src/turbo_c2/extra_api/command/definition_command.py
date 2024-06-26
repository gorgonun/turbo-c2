import os
from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar
from turbo_c2.extra_api.command.api_reference import ApiReference
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.interfaces.dynamic_command import DynamicCommand


Definition = TypeVar("Definition")
Resource = TypeVar("Resource")


@dataclass
class GetCommand(DynamicCommand[str | None, Resource]):
    resource_id: str | None
    api_identifier: str
    api_path: str

# FIXME: separate list from get
@dataclass
class ListCommand(DynamicCommand[None, Resource]):
    api_identifier: str
    api_path: str


@dataclass
class SetCommand(DynamicCommand[Tuple[Resource, str, bool], None]):
    resource: Resource
    resource_id: str
    fail_if_exists: bool
    api_identifier: str
    api_path: str


class DefinitionCommand(Generic[Definition, Resource]):
    api_identifier: str
    api_path: str

    @classmethod
    def get_api_reference(cls):
        return ApiReference(cls.api_identifier, cls.api_path)
    
    @classmethod
    def get_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "get")
    
    @classmethod
    def set_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "set")
    
    @classmethod
    def list_command_path(cls):
        return CommandPath(cls.api_identifier, cls.api_path, "list")

    @classmethod
    def get(cls, resource_id: str | None = None) -> DynamicCommand[str | None, Resource]:
        return GetCommand(
            resource_id=resource_id, api_identifier=cls.api_identifier, api_path=os.path.join(cls.api_path, "get")
        )
    
    @classmethod
    def list(cls) -> DynamicCommand[None, list[Resource]]:
        return ListCommand(api_identifier=cls.api_identifier, api_path=os.path.join(cls.api_path, "list"))

    @classmethod
    def set(cls, resource: Resource, resource_id: str, fail_if_exists = True) -> DynamicCommand[Tuple[Resource, str], None]:
        return SetCommand(
            resource=resource,
            resource_id=resource_id,
            fail_if_exists=fail_if_exists,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "set"),
        )
