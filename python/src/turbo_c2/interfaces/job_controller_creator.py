import abc
from typing import Any
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.interfaces.resource_creator import ResourceCreator
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class JobControllerCreator(ResourceCreator[JobController], NeedsCentralApi):
    @abc.abstractmethod
    async def create(
        self,
        definition: JobInstance,
        meta: dict[str, Any] | None = None,
    ) -> JobController:
        pass
