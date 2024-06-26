from pydantic import BaseModel
from turbo_c2.domain.job.job_instance_data_with_id import JobInstanceDataWithId


class ExternalJobGroupDefinition(BaseModel):
    resource_id: str
    name: str
    group_path: str
    job_instances_data: dict[str, JobInstanceDataWithId] = {}
