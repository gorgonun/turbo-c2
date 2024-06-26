import functools
import os
from typing import Hashable
from turbo_c2.external_api.default_external_api import DefaultExternalApi
from turbo_c2.helpers.file_cursor_utils import delete_file, delete_recursive
from turbo_c2.helpers.local_storage_json_path_mapping import LocalStorageJsonPathMapping
from turbo_c2.helpers.path_mapping import PathMapping
from turbo_c2.interfaces.external_apis.object_storage_external_api import ObjectStorageExternalApi


class LocalStorageExternalApi(ObjectStorageExternalApi, DefaultExternalApi[bytes, bytes]):

    def __init__(
        self, api_identifier: str, api_base_path: str, meta: PathMapping | None = None, deletion_meta: PathMapping | None = None
    ) -> None:
        super().__init__(api_identifier)
        self.__api_base_path = api_base_path
        self.__meta = meta or LocalStorageJsonPathMapping(api_base_path, "metadata")
        self.__deletion_meta = deletion_meta or LocalStorageJsonPathMapping(api_base_path, "deletion_metadata")

    @property
    def api_base_path(self):
        return self.__api_base_path
    
    @property
    def meta(self):
        return self.__meta
    
    @property
    def deletion_meta(self):
        return self.__deletion_meta

    async def get_object_reference(
        self, obj_identifiers: list[Hashable]
    ) -> bytes | None:
        obj_metadata = await self.__meta.get_resource(obj_identifiers)
        if not obj_metadata:
            return None

        obj_path = os.path.join(self.__api_base_path, obj_metadata["relative_path"])

        try:
            with open(obj_path, "rb") as f:
                return f.read()

        except FileNotFoundError:
            return None

    async def put_remote_object_reference(
        self, obj_identifiers: list[str], reference: bytes
    ):
        obj_metadata = await self.__meta.get_resource(obj_identifiers)
        if not obj_metadata:
            obj_metadata = {"relative_path": os.path.join(*obj_identifiers)}
            await self.__meta.put_resource(obj_identifiers, obj_metadata)

        obj_path = os.path.join(self.__api_base_path, obj_metadata["relative_path"])

        os.makedirs(os.path.dirname(obj_path), exist_ok=True)

        with open(obj_path, "wb") as f:
            f.write(reference)

    async def delete_item(self, obj_identifiers: list[Hashable]):
        obj_metadata = await self.__meta.get_resource(obj_identifiers)
        if not obj_metadata:
            return
        
        await self.__deletion_meta.put_resource(obj_identifiers, obj_metadata)
        deleted_keys = await self.__meta.delete_item(obj_identifiers)

        obj_path = os.path.join(self.__api_base_path, obj_metadata["relative_path"])

        delete_file(obj_path)
        delete_recursive(os.path.dirname(obj_path), deleted_keys)

        await self.__deletion_meta.delete_item(obj_identifiers)

    async def list_objects(
        self,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ) -> list[tuple[list[str], bytes]]:
        objs_meta = await self.__meta.get_all_resources(prefix, suffix, matches)

        result = []

        for meta_path, meta_obj in objs_meta:
            obj_path = meta_obj["relative_path"]

            obj = await self.get_object_reference(obj_path.split("/"))

            if not obj:
                raise FileNotFoundError(f"Object {obj_path} not found")

            result.append((meta_path, obj))

        return result

    def __reduce__(self):
        return (
            functools.partial(
                LocalStorageExternalApi,
                self.api_identifier,
                self.__api_base_path,
                self.__meta,
                self.__deletion_meta,
            ),
            tuple(),
        )
