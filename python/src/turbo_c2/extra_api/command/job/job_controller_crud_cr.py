from turbo_c2.extra_api.command.crud_client_resource_command import CrudClientResourceCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.jobs.job_instance import JobInstance


class JobControllerCrudCR(CrudClientResourceCommand[JobInstance, JobController, JobApi]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_controllers/controller"
