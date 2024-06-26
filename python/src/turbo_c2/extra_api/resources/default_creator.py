from typing import Any, TypeVar
from turbo_c2.interfaces.resource_creator import ResourceCreator


T = TypeVar("T")


class DefaultCreator(ResourceCreator[T]):
    async def create(self, definition: T, meta: dict[str, Any]):
        if getattr(definition, "meta", None) and isinstance(definition.meta, dict):
            definition.meta.update(meta)

        return definition
