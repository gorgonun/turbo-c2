from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Generic, TypeVar

from turbo_c2.jobs.dynamic_job.dynamic_job_helper_api import DynamicJobHelperApi


JOB_INPUT = TypeVar("JOB_INPUT")
T = TypeVar("T")


# FIXME: It should not depends on dynamic job
@dataclass
class JobContentParameter(Generic[JOB_INPUT, T]):
    after_send_to_output: Callable[[JOB_INPUT, T, DynamicJobHelperApi], Coroutine[Any, Any, None]] | None = None
