from dataclasses import dataclass
import functools
from types import SimpleNamespace
from typing import Any, Callable, Generic, TypeVar
from turbo_c2.mixin.has_id import HasId


T = TypeVar("T")


@dataclass(eq=False, kw_only=True)
class JobDefinition(Generic[T], HasId):
    name: str
    description: str | None
    run_function: Callable[..., T]
    args: list[Any]
    wait_time: int
    single_run: bool
    kwargs: dict[str, Any]
    meta: dict[str, Any]
    iterable_chunk_size: int
    on_init: Callable[[SimpleNamespace], None] | None
    disable_content_wrap: bool

    @property
    def resource_id(self) -> str:
        return self.name
    
    def __reduce__(self):
        return functools.partial(self.__class__, **{
            "name": self.name,
            "description": self.description,
            "run_function": self.run_function,
            "args": self.args,
            "wait_time": self.wait_time,
            "single_run": self.single_run,
            "kwargs": self.kwargs,
            "meta": self.meta,
            "iterable_chunk_size": self.iterable_chunk_size,
            "on_init": self.on_init,
            "disable_content_wrap": self.disable_content_wrap
        }), tuple()
