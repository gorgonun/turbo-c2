from typing import Any, TypeVar

from turbo_c2.interfaces.external_api import ExternalApi


T = TypeVar("T")
U = TypeVar("U")


class DefaultExternalApi(ExternalApi[T, U]):

    def __init__(self, api_identifier: str) -> None:
        self.__api_identifier = api_identifier

    @property
    def api_identifier(self):
        return self.__api_identifier
    
    @property
    def deletion_base_path(self):
        return f"delete_{self.api_identifier}"

    async def get_api_identifier(self):
        return self.__api_identifier

    async def get_object_reference_by_path(self, obj_path: str):
        return self.get_object_reference(obj_path.split("/"))

    async def put_remote_object_reference_by_path(self, obj_path: str, reference: Any):
        return self.put_remote_object_reference(obj_path.split("/"), reference)
