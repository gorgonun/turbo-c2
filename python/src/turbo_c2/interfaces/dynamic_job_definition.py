from dataclasses import dataclass
import functools
from types import SimpleNamespace
from typing import Any, Callable, TypeVar
from turbo_c2.jobs.job_input_spec import JobInputSpec
from turbo_c2.interfaces.job_definition import JobDefinition


T = TypeVar("T")


@dataclass(eq=False)
class DynamicJobDefinition(JobDefinition[T]):
    name: str
    description: str | None
    run_function: Callable[..., T]
    args: list[Any]
    wait_time: int
    single_run: bool
    tuple_result_is_single_value: bool
    clients_with_context: dict[str, Any] | None
    kwargs: dict[str, Any]
    spec: JobInputSpec | None
    on_init: Callable[[SimpleNamespace], None] | None
    disable_content_wrap: bool

    def __reduce__(self):
        return functools.partial(self.__class__, **{
            "name": self.name,
            "description": self.description,
            "run_function": self.run_function,
            "args": self.args,
            "wait_time": self.wait_time,
            "single_run": self.single_run,
            "tuple_result_is_single_value": self.tuple_result_is_single_value,
            "clients_with_context": self.clients_with_context,
            "kwargs": self.kwargs,
            "spec": self.spec,
            "on_init": self.on_init,
            "meta": self.meta,
            "iterable_chunk_size": self.iterable_chunk_size,
            "disable_content_wrap": self.disable_content_wrap
        }), tuple()
