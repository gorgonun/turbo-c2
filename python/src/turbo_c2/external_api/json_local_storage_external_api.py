import functools
import json
from typing import Hashable
from turbo_c2.external_api.local_storage_external_api import LocalStorageExternalApi


class JsonLocalStorageExternalApi(LocalStorageExternalApi):

    async def get_object_reference(self, obj_identifiers: list[Hashable]):
        obj = await super().get_object_reference(obj_identifiers)

        if obj is None:
            return None

        return json.loads(obj)

    async def put_remote_object_reference(
        self, obj_identifiers: list[str], reference: dict
    ):
        await super().put_remote_object_reference(
            obj_identifiers, json.dumps(reference).encode("utf-8")
        )

    def __reduce__(self):
        return (
            functools.partial(
                JsonLocalStorageExternalApi,
                self.api_identifier,
                self.api_base_path,
                self.meta,
                self.deletion_meta,
            ),
            tuple(),
        )
