from turbo_c2.domain.object_storage.json_turbo_object_model import JsonTurboObjectModel
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.object_storage.object_storage_enum import ObjectStorageEnum


class JTMResource(CrudCommand[JsonTurboObjectModel, JsonTurboObjectModel]):
    api_identifier = ObjectStorageEnum.API_ID.value
    api_path = "jtm_objects"
