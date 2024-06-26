from typing import Any
from pydantic import BaseModel

from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode


class MovePositionDefinitionRequest(BaseModel):
    x: float
    y: float


class JobInstanceDataRequest(BaseModel):
    job_definition_id: str
    replicas: int
    replication_mode: RemoteJobReplicaMode
    read_only: bool
    group_path: str
    input_queue_reference: str | None = None
    extra_queues_references: list[str] = []
    output_queues_references: list[str] = []
    parameters: dict[str, Any] | None = None
    name: str | None = None
    position_definition: MovePositionDefinitionRequest | None = None
    layout_id: str | None = None
