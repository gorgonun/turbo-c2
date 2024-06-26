from dataclasses import dataclass
from turbo_c2.interfaces.job_api import JobApi


@dataclass
class NewJobCreated:
    job_api: JobApi
