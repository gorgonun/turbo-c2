from typing import Any
from turbo_c2.globals.ebf_global import scheduler_globals
from turbo_c2.jobs.default_job_creator import DefaultJobCreator
from turbo_c2.jobs.job_definition_with_settings import JobDefinitionWithSettings
from turbo_c2.jobs.local_job_controller import LocalJobController


class LocalJobCreator(DefaultJobCreator):
    def create(self, job_definition: JobDefinitionWithSettings, meta: dict[str, Any] | None = None):
        job_type = scheduler_globals.get_job_for_definition(job_definition.job_definition)
        job = job_type(job_definition.job_definition)
        return LocalJobController(job_definition.job_definition)
