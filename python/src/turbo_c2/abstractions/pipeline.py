import random
from typing import Any, Callable, cast
from turbo_c2.decorators.node import node
from turbo_c2.decorators.job import job
from turbo_c2.globals.ebf_global import DefaultSchedulerGlobals
from turbo_c2.jobs.job import Job
from turbo_c2.jobs.remote_job import RemoteJob
from turbo_c2.abstractions.pipeline_node import PipelineNode
from turbo_c2.queues.queue_definition import QueueDefinition


class Pipeline():
    def __init__(self, nodes_or_jobs: list[PipelineNode | Job] | None=None) -> None:
        self.nodes = self.all_nodes(nodes_or_jobs) if nodes_or_jobs else []

        if self.nodes:
            self.prepare(*self.nodes)

    def all_nodes(self, nodes_or_jobs: list[PipelineNode | Job]) -> list[PipelineNode]:
        nodes: list[PipelineNode] = []

        for node_or_job in nodes_or_jobs:
            if isinstance(node_or_job, PipelineNode):
                nodes.append(node_or_job)
            else:
                nodes.append(PipelineNode([node_or_job]))

        return nodes
    
    # FIXME: Redirect all to one queue instead to multiple queues
    def node_job(self, *args: Any, **kwds: Any) -> Any:
        def wrapped(func: Callable[..., Any]):
            new_job = job(*args, **kwds)(func)
            new_node = PipelineNode(jobs=[new_job])
            needs_preparation = []

            if self.nodes:
                self.nodes[-1].add_edge(new_node)
                needs_preparation.append(self.nodes[-1])

            needs_preparation.append(new_node)

            self.nodes.append(new_node)
            self.prepare(*needs_preparation)
            return new_job

        return wrapped
    
    def node(self, *args: Any, **kwds: Any) -> Any:
        def wrapped(func: Callable[..., Any]):
            new_node = node(*args, **kwds)(func)
            self.nodes.append(new_node)
            self.prepare(new_node)
            return new_node

        return wrapped
    
    # TODO: Implement
    def before_all(self, *args: Any, **kwds: Any) -> Any:
        pass

    def after_all(self, *args: Any, **kwds: Any) -> Any:
        pass

    def before_each(self, *args: Any, **kwds: Any) -> Any:
        pass

    def after_each(self, *args: Any, **kwds: Any) -> Any:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
    
    def prepare(self, *nodes: PipelineNode) -> None:
        def _prepare(target_node: PipelineNode):
            for job in target_node.jobs:
                job = cast(RemoteJob, job)
                if target_node.edge:
                    if not job.get_outputs():
                        queue_name = job.get_name() + "_queue_" + str(random.randint(0, 100000))
                        queue = QueueDefinition(queue_name)
                        job.add_outputs({queue_name: queue})

                    mapping = job.get_outputs_mapping()
                    for edge_job in target_node.edge.jobs:
                        edge_job = cast(RemoteJob, edge_job)
                        edge_job.add_queues(mapping)

                DefaultSchedulerGlobals.add_job(job)

        for node in nodes:
            target_node: PipelineNode | None = node
            while target_node:
                _prepare(target_node)
                target_node = target_node.edge
