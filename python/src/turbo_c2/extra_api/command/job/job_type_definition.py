from typing import Hashable
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.jobs.job import Job


class JobTypeDefinition(DefinitionCommand[Hashable, Job]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_types"
