from typing import Any
from turbo_c2.domain.gui.layout_definition import LayoutDefinition
from turbo_c2.interfaces.resource_creator import ResourceCreator


class LayoutDefinitionCreator(ResourceCreator[LayoutDefinition]):
    async def create(self, definition: LayoutDefinition, meta: dict[str, Any]):
        definition.meta = {**definition.meta, **meta}
        return definition
