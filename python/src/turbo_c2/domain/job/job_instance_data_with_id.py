from typing import Generic, TypeVar
from pydantic import BaseModel
from turbo_c2.abstractions.job_parameter import JobParameter

from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode


T = TypeVar("T", bound=JobParameter)


class JobInstanceDataWithId(BaseModel, Generic[T]):
    instance_resource_id: str
    job_definition_id: str
    replicas: int
    replication_mode: RemoteJobReplicaMode
    read_only: bool
    group_path: str
    input_queue_reference: str | None = None
    extra_queues_references: list[str] = []
    output_queues_references: list[str] = []
    parameters: T | None = None
    name: str | None = None

    @property
    def resource_id(self):
        return self.instance_resource_id
    
    @resource_id.setter
    def resource_id(self, value):
        self.instance_resource_id = value
