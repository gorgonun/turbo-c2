from __future__ import annotations
from dataclasses import dataclass, field
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.jobs.job_instance import JobInstance


@dataclass
class NodeChild:
    node: Node
    edge: str | None


@dataclass(unsafe_hash=True)
class Node:
    instance: JobInstance
    children: list[NodeChild] = field(default_factory=list, hash=False)


@dataclass
class QueueInputsOutputsMapping:
    inputs: list[JobInstance] = field(default_factory=list)
    outputs: list[JobInstance] = field(default_factory=list)


@dataclass
class GroupNodes:
    is_cycle: bool
    is_isolated: bool
    external_input_queues: list[str]
    external_output_queues: list[str]
    nodes: Node


def get_set():
    return set()


async def get_job_group_nodes(job_group: JobGroupWithInstances) -> list[GroupNodes]:
    # First it get all job isntances from job group and creates an index with the queue name as key and the job that produces to the queue as inputs and the jobs that consume as outputs
    # Ex:
    #   index = {
    #       "queue1": {
    #           "inputs": [job1],
    #           "outputs": [job2, job3]
    #       },
    #       "queue2": {
    #           "inputs": [job2],
    #           "outputs": []
    #       },
    #    }
    # Also, it creates a list of isolated nodes (nodes that don't have input or output queues). The isolated are ready to go.
    # After that, it creates a list of first nodes (nodes that don't have input queues, but have output queues). The first nodes will be used to locate DAG style jobs.
    # It also creates a list of reference to job instances. It will be used to detect cycles, because on a cycle there is no first node. Those instances on the cycle won't be referenced, then we need to iterate over them until all are referenced.
    # After that, it needs to iterate over the first nodes and get all the nodes that are connected to it. It will be done using the index. It will be done recursively.
    # Ex:
    #   index = {
    #       "queue1": {
    #           "inputs": [job1],
    #           "outputs": [job2, job3]
    #       },
    #       "queue2": {
    #           "inputs": [job2],
    #           "outputs": []
    #       },
    #    }
    #   first_nodes = [job1]
    # As job1 sends to queue1, and queue1 has as consumers job2 and job3, we can say that job1 -> [job2, job3], that will be [(job1, [job2, job3])]
    # The same result can be describe as (job1, [(job2, []), (job3, [])])
    # After that, we need to identify the cycles. We can do that by checking if the node was already referenced on a previous iteration. If it wasn't, it means that it is a cycle.
    # For the cycles we need to apply the same algorithm, but there is no first node to start.
    isolated_nodes: list[JobInstance] = []

    index: dict[str, QueueInputsOutputsMapping] = {}
    # They are first when thinking about DAGs, but on cycles there is no first node
    first_nodes: list[JobInstance] = []
    # Job instances checks if the job was referenced before
    job_instances: set[JobInstance] = get_set()
    external_input_queues = get_set()
    external_output_queues = get_set()

    for job_instance in job_group.job_instances:
        # If no input, it always will be the first node or an isolated node
        if not await job_instance.get_input_queue_name():
            if not await job_instance.get_output_queues_names():
                # Isolated nodes don't need to be referenced
                isolated_nodes.append(job_instance)
                continue
            # First nodes won't be searched
            first_nodes.append(job_instance)
            job_instances.add(job_instance)
        else:
            job_instances.add(job_instance)
            # Middle nodes will be searched
            index.setdefault(
                await job_instance.get_input_queue_name(), QueueInputsOutputsMapping()
            ).outputs.append(job_instance)

        for queue in await job_instance.get_output_queues_names():
            index.setdefault(queue, QueueInputsOutputsMapping()).inputs.append(
                job_instance
            )

    # The first nodes can be on queues that just has outputs, but no inputs, as they can be from another group
    for queue, mapping in index.items():
        if not mapping.inputs:
            first_nodes.extend(mapping.outputs)
            external_input_queues.add(queue)

        elif not mapping.outputs:
            external_output_queues.add(queue)

    async def get_node(instance: JobInstance, cache: set):
        if instance in cache:
            return Node(instance, [])

        cache.add(instance)

        result = []

        for queue in await instance.get_output_queues_names():
            for consumer in index[queue].outputs:
                instance_nodes = await get_node(consumer, cache)
                result.append(NodeChild(instance_nodes, queue))

        # It needs to return [], if there are no instances connected to the node, or a repeated instance, if there is a cycle on the middle
        return Node(instance, result)

    # The instances can be repeated between nodes, but can't be repeated on the same node
    caches = [get_set() for _ in range(len(first_nodes))]

    nodes = [
        GroupNodes(
            is_cycle=False,
            is_isolated=False,
            **{
                "nodes": await get_node(job_instance, caches[i]),
                "external_input_queues": list(
                    external_input_queues.intersection(
                        (await job_instance.get_input_queue_name()) or []
                    )
                ),
                "external_output_queues": list(
                    external_output_queues.intersection(
                        *(await job_instance.get_output_queues_names())
                    )
                ),
            },
        )
        for (i, job_instance) in enumerate(first_nodes)
    ]

    # We union all caches and remove it from job_instances to detect the ones that were never referenced
    job_instances -= get_set().union(*caches)

    # We need to iterate over the job instances that were never referenced and add it to the nodes. They don't have a first element, so any element will be the first
    while job_instances:
        cycle_cache = get_set()
        target_instance = job_instances.pop()
        nodes.append(
            GroupNodes(
                is_cycle=True,
                is_isolated=False,
                nodes=await get_node(target_instance, cycle_cache),
                external_input_queues=list(
                    external_input_queues.intersection(
                        await target_instance.get_input_queue_name()
                    )
                ),
                external_output_queues=list(
                    external_output_queues.intersection(
                        *(await target_instance.get_output_queues_names())
                    )
                ),
            )
        )
        job_instances -= cycle_cache

    return [
        *nodes,
        *[
            GroupNodes(
                is_cycle=False,
                is_isolated=True,
                nodes=Node(node),
                external_input_queues=[],
                external_output_queues=[],
            )
            for node in isolated_nodes
        ],
    ]


# def serialize_group_nodes(group_nodes: list[GroupNodes]) -> list[dict]:
#     def serialize_node
