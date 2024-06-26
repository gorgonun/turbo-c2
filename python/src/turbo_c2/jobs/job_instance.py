import functools
import os
from typing import Generic, TypeVar
from dataclasses import dataclass, field
import uuid
from turbo_c2.abstractions.job_parameter import JobParameter
from turbo_c2.interfaces.job_definition import JobDefinition
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode

from turbo_c2.mixin.has_id import HasId
from turbo_c2.queues.queue_reference import QueueReference


T = TypeVar("T")
U = TypeVar("U", bound=JobParameter)


@dataclass(eq=False)
class JobInstance(HasId, Generic[T, U]):
    # Id = resource_id
    # or
    # (job_definition_id + group_path + (replication_mode == FOLLOW_QUEUE ? extra_queues_references : [input_queue_reference]) + output_queues_references)
    job_definition: JobDefinition[T]
    replicas: int
    replication_mode: RemoteJobReplicaMode
    read_only: bool
    group_path: str
    instance_resource_id: str = field(default_factory=lambda: f"JobInstance_{uuid.uuid4().hex}")
    input_queue_reference: QueueReference | None = None
    extra_queues_references: list[QueueReference] = field(default_factory=list)
    output_queues_references: list[QueueReference] = field(default_factory=list)
    parameters: U | None = None
    name: str | None = None
    num_cpus: float | None = None
    memory: int | None = None
    scheduling_strategy: str = "SPREAD"
    buffer_size: int = 100
    accumulate_write_seconds: int = 0.1

    # If true, the job needs to have only one output queue. It cannot send to self and to another queue, as this is two output queues.
    job_needs_to_match_input_with_output: bool = False

    @property
    def resource_id(self):
        return self.instance_resource_id
    
    @property
    def job_definition_id(self):
        return self.job_definition.resource_id
    
    @property
    def id_queues(self):
        if self.replication_mode == RemoteJobReplicaMode.FOLLOW_QUEUE:
            return self.extra_queues_references, self.output_queues_references
        else:
            input_queue_reference = [self.input_queue_reference] if self.input_queue_reference else []
            return input_queue_reference, self.output_queues_references
    
    @property
    def derivated_id(self) -> str:
        input_queues, output_queues = self.id_queues

        return os.path.join(
            self.name or '',
            self.job_definition_id,
            self.group_path,
            self.replication_mode.value,
            ",".join(map(lambda x: str(x.identifier) if isinstance(x, QueueReference) else x, input_queues)),
            ",".join(map(lambda x: str(x.identifier) if isinstance(x, QueueReference) else x, output_queues))
        )
    
    def get_name(self):
        return self.name or self.job_definition.name

    async def get_input_queue_name(self):
        if self.input_queue_reference is None:
            return None
        return self.input_queue_reference.identifier
    
    async def get_extra_queues_names(self):
        return [x.identifier for x in self.extra_queues_references]
    
    async def get_output_queues_names(self):
        return [x.identifier for x in self.output_queues_references]
    
    def __reduce__(self):
        return functools.partial(
            self.__class__,
            **{
                "job_definition": self.job_definition,
                "replicas": self.replicas,
                "replication_mode": self.replication_mode,
                "read_only": self.read_only,
                "group_path": self.group_path,
                "instance_resource_id": self.instance_resource_id,
                "input_queue_reference": self.input_queue_reference,
                "extra_queues_references": self.extra_queues_references,
                "output_queues_references": self.output_queues_references,
                "parameters": self.parameters,
                "name": self.name,
                "num_cpus": self.num_cpus,
                "memory": self.memory,
                "scheduling_strategy": self.scheduling_strategy
            }
        ), tuple()
