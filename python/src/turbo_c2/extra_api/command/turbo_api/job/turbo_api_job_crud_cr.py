from turbo_c2.extra_api.command.crud_client_resource_command import CrudClientResourceCommand
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.jobs.job_definition_with_settings import JobDefinitionWithSettings


class TurboApiJobCrudCR(CrudClientResourceCommand[JobDefinitionWithSettings, JobController, JobApi]):
    api_identifier = "turbo"
    api_path = "jobs"
