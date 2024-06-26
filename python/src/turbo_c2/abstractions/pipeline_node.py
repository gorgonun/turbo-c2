from __future__ import annotations
from typing import Any, Callable

from turbo_c2.decorators.job import job


class PipelineNode:
    def __init__(self, jobs: list[Any] | None=None, edge: PipelineNode | None=None, name: str | None=None, description: str | None=None):
        self.name = name
        self.description = description
        self.jobs: list[Any] = jobs or []
        self.edge = edge

    def job(self, *args: Any, **kwds: Any) -> Any:
        def wrapped(func: Callable[..., Any]):
            new_job = job(*args, **kwds)(func)
            self.jobs.append(new_job)
            return new_job

        return wrapped

    def add_edge(self, edge: PipelineNode):
        self.edge = edge
        return self

    def __str__(self):
        return "PipelineDefinition(name={}, description={}, jobs={})".format(
            self.name, self.description, self.jobs
        )

    def __repr__(self):
        return self.__str__()
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
