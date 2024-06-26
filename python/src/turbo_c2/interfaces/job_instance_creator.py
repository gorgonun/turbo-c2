import abc
from typing import Any
from turbo_c2.interfaces.resource_creator import ResourceCreator
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class JobInstanceCreator(ResourceCreator[JobInstance], NeedsCentralApi):
    @abc.abstractmethod
    async def create(
        self,
        definition: JobInstanceData,
        meta: dict[str, Any] | None = None,
    ) -> list[JobInstance]:
        pass
