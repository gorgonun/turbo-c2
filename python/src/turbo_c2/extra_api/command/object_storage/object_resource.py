from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.object_storage.object_storage_enum import ObjectStorageEnum


class ObjectResource(CrudCommand[bytes, bytes]):
    api_identifier = ObjectStorageEnum.API_ID.value
    api_path = "objects"
