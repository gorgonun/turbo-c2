from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.object_storage.object_storage_enum import ObjectStorageEnum
from turbo_c2.helpers.types import PJSON


class JsonResource(CrudCommand[PJSON, PJSON]):
    api_identifier = ObjectStorageEnum.API_ID.value
    api_path = "json_objects"
