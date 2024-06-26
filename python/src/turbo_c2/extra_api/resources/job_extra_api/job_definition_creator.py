from dataclasses import replace
from typing import Any
from turbo_c2.interfaces.job_definition import JobDefinition
from turbo_c2.interfaces.resource_creator import ResourceCreator


class JobDefinitionCreator(ResourceCreator[JobDefinition]):
    async def create(self, definition: JobDefinition, meta: dict[str, Any]):
        return replace(definition, meta={**definition.meta, **meta})
