from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.interfaces.job_definition import JobDefinition


class JobDefinitionCreatorDefinition(DefinitionCommand[JobDefinition, JobDefinition]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_definitions/creators"
