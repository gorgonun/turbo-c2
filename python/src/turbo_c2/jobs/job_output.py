from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from turbo_c2.jobs.job_content_parameter import JobContentParameter


JOB_INPUT = TypeVar("JOB_INPUT")
T = TypeVar("T")

@dataclass
class JobOutput(Generic[JOB_INPUT, T]):
    content: T
    content_parameters: dict[str, Any] = field(default_factory=dict)
    job_content_parameters: list[JobContentParameter[JOB_INPUT, T]] = field(default_factory=list)
