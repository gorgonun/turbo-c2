from typing import Any
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.in_memory_object_storage.in_memory_object_storage_enum import InMemoryObjectStorageEnum


class MemoryResource(CrudCommand[Any, Any]):
    api_identifier = InMemoryObjectStorageEnum.API_ID.value
    api_path = "objects"
