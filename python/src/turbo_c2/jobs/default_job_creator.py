import abc
from typing import Any
import uuid
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller_creator import JobControllerCreator
from turbo_c2.jobs.job_definition_with_settings import JobDefinitionWithSettings
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class DefaultJobCreator(JobControllerCreator, NeedsCentralApi):
    def __init__(self, identifier: str | None = None) -> None:
        self.__identifier = identifier or "JobCreator_" + uuid.uuid4().hex[:8]
        super().__init__()

    @property
    def identifier(self):
        return self.__identifier

    @abc.abstractmethod
    async def create(
        self,
        job_definition: JobDefinitionWithSettings,
        meta: dict[str, Any] | None = None,
    ) -> JobApi:
        pass
