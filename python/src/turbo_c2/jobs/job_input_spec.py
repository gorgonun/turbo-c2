from dataclasses import dataclass
from typing import Type

from turbo_c2.abstractions.job_parameter import JobParameter


@dataclass
class JobInputSpecQueuesMultipleSpec:
    description: str | None
    quantity: int | None


@dataclass
class JobInputSpecQueuesSingleSpec:
    description: str | None


@dataclass
class JobInputSpecQueuesSpec:
    input_queue: JobInputSpecQueuesSingleSpec
    extra_queues: JobInputSpecQueuesMultipleSpec
    output_queues: JobInputSpecQueuesMultipleSpec


@dataclass
class JobInputSpec:
    queues: JobInputSpecQueuesSpec
    parameters: Type[JobParameter] | None
