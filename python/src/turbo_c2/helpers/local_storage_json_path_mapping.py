import functools
import json
import os
from typing import Hashable
from turbo_c2.helpers.path_mapping import PathMapping


class LocalStorageJsonPathMapping():

    def __init__(
        self, file_path: str, file_name: str | None = None, data: PathMapping | None = None
    ) -> None:
        self.__file_name = file_name or "metadata"
        self.__file_path = file_path
        self.__data = data or self.load_meta()

    @property
    def file_path(self):
        return self.__file_path
    
    @property
    def file_name(self):
        return self.__file_name
    
    @property
    def data(self):
        return self.__data
    
    @property
    def data_file_path(self):
        return f"{self.__file_path}/{self.__file_name}.json"

    def load_meta(self) -> PathMapping:
        try:
            with open(self.data_file_path, "r") as f:
                return PathMapping(json.loads(f.read()))

        except FileNotFoundError:
            return PathMapping()

    async def get_resource(
        self, obj_identifiers: list[Hashable]
    ) -> bytes | None:
        return self.__data.get_resource(obj_identifiers)

    async def put_resource(
        self, obj_identifiers: list[str], reference: bytes
    ):
        self.__data.put_resource(obj_identifiers, reference)
        await self.dump_meta()

    async def dump_meta(self):
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
        with open(self.data_file_path, "w") as f:
            f.write(json.dumps(self.__data.mapping))

    async def delete_item(self, obj_identifiers: list[Hashable]):
        result = self.__data.delete_item(obj_identifiers)
        await self.dump_meta()
        return result

    async def get_all_resources(
        self,
        prefix: str | None = None,
        suffix: str | None = None,
        matches: str | None = None,
    ) -> list[tuple[list[str], bytes]]:
        return self.__data.get_all_resources(prefix, suffix, matches)

    def __reduce__(self):
        return (
            functools.partial(
                LocalStorageJsonPathMapping,
                self.file_path,
                self.file_name,
                self.__data,
            ),
            tuple(),
        )
