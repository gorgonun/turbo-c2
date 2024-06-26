from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.interfaces.job_controller_creator import JobControllerCreator


class JobInstanceCreatorDefinition(DefinitionCommand[str, JobControllerCreator]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_instances/creators"
