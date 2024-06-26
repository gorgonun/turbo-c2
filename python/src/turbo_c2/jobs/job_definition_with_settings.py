from dataclasses import dataclass

from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.interfaces.job_definition import JobDefinition


@dataclass
class JobDefinitionWithSettings:
    job_definition: JobDefinition
