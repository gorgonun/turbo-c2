from typing import Type
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.interfaces.job_api import JobApi


class JobApiDefinition(DefinitionCommand[str, Type[JobApi]]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_apis/definitions"
