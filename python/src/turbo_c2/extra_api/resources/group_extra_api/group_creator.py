from dataclasses import replace
from typing import Any
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.interfaces.resource_creator import ResourceCreator


class GroupCreator(ResourceCreator[JobGroup]):
    async def create(self, definition: JobGroup, meta: dict[str, Any]):
        return replace(definition, meta={**definition.meta, **meta})
