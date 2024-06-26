from typing import Callable
from turbo_c2.jobs.job import Job
from turbo_c2.abstractions.pipeline_node import PipelineNode


def node():
    def wrapped(func: Callable[[PipelineNode], list[Job]]):
        node = PipelineNode()
        func(node)
        return node
    return wrapped
