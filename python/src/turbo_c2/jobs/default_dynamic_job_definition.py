from dataclasses import dataclass, field
from typing import Any, TypeVar
from turbo_c2.jobs.job_input_spec import JobInputSpec

from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition


T = TypeVar("T")


@dataclass
class DefaultDynamicJobDefinition(DynamicJobDefinition[T]):
    description: str | None = None
    args: list[Any] = field(default_factory=list)
    input_queue_reference: list[QueueReference] | None = None
    extra_queues_references: list[QueueReference] | None = None
    output_queues_references: list[QueueReference] | None = None
    wait_time: int = 1
    single_run: bool = False
    tuple_result_is_single_value: bool = False
    clients_with_context: dict[str, Any] | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    parameters: JobInputSpec | None = None

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self.run_function(*self.args, *args, **self.kwargs, **kwargs)
