from dataclasses import dataclass, field
from typing import Generic, TypeVar
from turbo_c2.abstractions.job_parameter import JobParameter

from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.queues.queue_reference import QueueReference


PARAMETER = TypeVar("PARAMETER", bound=JobParameter)


@dataclass
class JobInstanceData(Generic[PARAMETER]):
    job_definition_id: str
    replicas: int
    replication_mode: RemoteJobReplicaMode
    read_only: bool
    group_path: str
    input_queue_reference: QueueReference | None = None
    extra_queues_references: list[QueueReference] = field(default_factory=list)
    output_queues_references: list[QueueReference] = field(default_factory=list)
    parameters: PARAMETER | None = None
    name: str | None = None
    num_cpus: float | None = None
    memory: int | None = None
    scheduling_strategy: str = "SPREAD"
