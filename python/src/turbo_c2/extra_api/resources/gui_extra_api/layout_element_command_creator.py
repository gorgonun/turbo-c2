from dataclasses import replace
from typing import Any
from turbo_c2.domain.gui.layout_element_command import LayoutElementCommand
from turbo_c2.interfaces.resource_creator import ResourceCreator


class LayoutElementCommandCreator(ResourceCreator[LayoutElementCommand]):
    async def create(self, definition: LayoutElementCommand, meta: dict[str, Any]):
        return replace(definition, meta={**definition.meta, **meta})
