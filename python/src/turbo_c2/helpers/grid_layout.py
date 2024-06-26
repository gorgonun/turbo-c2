import json
from typing import TypeVar
import graphviz
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.domain.gui.layout_definition import PositionDefinition, WindowDefinition
from turbo_c2.domain.gui.layout_element import LayoutElement

from turbo_c2.helpers.job_group_utils import GroupNodes, Node
from turbo_c2.jobs.edge_representation import EdgeRepresentation
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.node_representation import NodeRepresentation


D = TypeVar("D", bound=PositionDefinition)


class GridLayout:
    def __init__(self, name: str, description: str | None):
        self.graph = graphviz.Digraph(name, comment=description)
        self.__node_width = "4"
        self.__node_height = "2"
        self.representation_shape_mapping = {
            NodeRepresentation.ACTION: "box",
            NodeRepresentation.DECISION: "diamond",
        }

    async def load_graph(
        self,
        current_group: JobGroup,
        group_nodes: list[GroupNodes],
        sub_groups: list[tuple[JobGroup, GroupNodes]],
        groups_edge_mapping: dict[str, JobGroup],
        queue_group_instance_mapping: dict[str, list[tuple[JobGroup, JobInstance]]],
        layout_elements: list[LayoutElement],
        graph_definition: WindowDefinition | None = None,
    ):
        external_input_nodes: dict[str, list[JobInstance]] = {}
        external_output_nodes: dict[str, list[JobInstance]] = {}
        groups = set()

        async def traverse(
            node: Node,
            edge: tuple[str, str] | None,
            external_input_queues: set[str],
            external_output_queues: set[str],
        ):
            if len(node.children) > 0:
                for child in node.children:
                    await traverse(
                        child.node,
                        (child.edge, node.instance.resource_id),
                        external_input_queues,
                        external_output_queues,
                    )

            position = (
                self.get_pos_parameter_from_definition(
                    graph_definition.job_instances, node.instance.resource_id
                )
                if graph_definition
                else None
            )
            self.graph.node(
                node.instance.resource_id,
                label=node.instance.name or node.instance.resource_id,
                pos=position,
                width=self.__node_width,
                height=self.__node_height,
                representation=NodeRepresentation.ACTION.value,
            )

            instance_input_queue = await node.instance.get_input_queue_name()
            instance_output_queues = await node.instance.get_output_queues_names()

            for queue in external_input_queues.difference([instance_input_queue] or []):
                external_input_nodes.setdefault(queue, []).append(node.instance)

            for queue in external_output_queues.difference(instance_output_queues):
                external_output_nodes.setdefault(queue, []).append(node.instance)

            if edge:
                queue_name, edge_node_id = edge
                edge_position = (
                    self.get_pos_parameter_from_definition(
                        graph_definition.queues, queue_name
                    )
                    if graph_definition
                    else None
                )
                self.graph.edge(
                    node.instance.resource_id,
                    edge_node_id,
                    pos=edge_position,
                    representation=EdgeRepresentation.QUEUE.value,
                    resource_id=queue_name,
                )

        for group_node in group_nodes:
            await traverse(
                group_node.nodes,
                None,
                set(group_node.external_input_queues),
                set(group_node.external_output_queues),
            )

        for sub_group, group_nodes in sub_groups:
            position = (
                self.get_pos_parameter_from_definition(
                    graph_definition.sub_groups, sub_group.resource_id
                )
                if graph_definition
                else None
            )

            self.graph.node(
                sub_group.resource_id,
                label=sub_group.name,
                pos=position,
                width=self.__node_width,
                height=self.__node_height,
                representation=NodeRepresentation.GROUP.value,
            )

            for group_node in group_nodes:
                external_input_edges = [
                    (queue, external_output_nodes[queue])
                    for queue in group_node.external_input_queues
                ]
                external_output_edges = [
                    (queue, external_input_nodes[queue])
                    for queue in group_node.external_output_queues
                ]

                for queue, instances in external_input_edges + external_output_edges:
                    for instance in instances:
                        edge_position = (
                            self.get_pos_parameter_from_definition(
                                graph_definition.queues, queue
                            )
                            if graph_definition
                            else None
                        )
                        self.graph.edge(
                            instance.resource_id,
                            sub_group.resource_id,
                            pos=edge_position,
                            representation=EdgeRepresentation.QUEUE.value,
                            resource_id=queue,
                        )

        for queue, instances in external_input_nodes.items():
            external_data = queue_group_instance_mapping.get(queue)
            if external_data:
                groups = set()

                for external_group, external_instance in external_data:
                    if external_group.path not in groups:
                        groups.add(external_group.path)
                        position = (
                            self.get_pos_parameter_from_definition(
                                graph_definition.queues, queue
                            )
                            if graph_definition
                            else None
                        )
                        self.graph.node(
                            external_group.resource_id,
                            label=external_group.name,
                            pos=position,
                            width=self.__node_width,
                            height=self.__node_height,
                            representation=NodeRepresentation.GROUP.value,
                        )

                    for instance in instances:
                        self.graph.edge(
                            instance.resource_id,
                            external_group.resource_id,
                            pos=position,
                            representation=EdgeRepresentation.QUEUE.value,
                            resource_id=queue,
                        )

        for queue, instances in external_output_nodes.items():
            external_data = queue_group_instance_mapping.get(queue)
            if external_data:

                for external_group, external_instance in external_data:
                    if external_group.path not in groups:
                        groups.add(external_group.path)
                        position = (
                            self.get_pos_parameter_from_definition(
                                graph_definition.queues, queue
                            )
                            if graph_definition
                            else None
                        )
                        self.graph.node(
                            external_group.resource_id,
                            label=external_group.name,
                            pos=position,
                            width=self.__node_width,
                            height=self.__node_height,
                            representation=NodeRepresentation.GROUP.value,
                        )

                    for instance in instances:
                        self.graph.edge(
                            external_group.resource_id,
                            instance.resource_id,
                            pos=position,
                            representation=EdgeRepresentation.QUEUE.value,
                            resource_id=queue,
                        )

        for layout_element in layout_elements:
            shape = self.representation_shape_mapping.get(
                layout_element.representation, "box"
            )

            position = (
                self.get_pos_parameter_from_definition(
                    graph_definition.items, layout_element.resource_id
                )
                if graph_definition
                else None
            )
            self.graph.node(
                layout_element.resource_id,
                shape=shape,
                label=layout_element.resource_name or layout_element.resource_id,
                pos=position,
                width=self.__node_width,
                height=self.__node_height,
                representation=layout_element.representation.value,
            )

            for source in layout_element.sources or []:
                if source.target in groups_edge_mapping:
                    if groups_edge_mapping[source.target].path != current_group.path:
                        if groups_edge_mapping[source.target].path not in groups:
                            groups.add(groups_edge_mapping[source.target].path)
                            position = (
                                self.get_pos_parameter_from_definition(
                                    graph_definition.items, source.target
                                )
                                if graph_definition
                                else None
                            )
                            self.graph.node(
                                groups_edge_mapping[source.target].resource_id,
                                label=groups_edge_mapping[source.target].name,
                                pos=position,
                                width=self.__node_width,
                                height=self.__node_height,
                                representation=NodeRepresentation.GROUP.value,
                            )

                        else:
                            raise RuntimeError(
                                f"Group {groups_edge_mapping[source.target].path} is not in the graph"
                            )

                        edge_name = groups_edge_mapping[source.target].resource_id

                    else:
                        edge_name = source.target

                    self.graph.edge(
                        edge_name,
                        layout_element.resource_id,
                        pos=position,
                        representation=source.representation.value,
                        resource_id=f"{layout_element.resource_id}_{edge_name}",
                    )

            for destination in layout_element.destinations or []:
                if destination.target in groups_edge_mapping:
                    if (
                        groups_edge_mapping[destination.target].path
                        != current_group.path
                    ):
                        if groups_edge_mapping[destination.target].path not in groups:
                            groups.add(groups_edge_mapping[destination.target].path)
                            position = (
                                self.get_pos_parameter_from_definition(
                                    graph_definition.items, destination.target
                                )
                                if graph_definition
                                else None
                            )
                            self.graph.node(
                                groups_edge_mapping[destination.target].resource_id,
                                label=groups_edge_mapping[destination.target].name,
                                pos=position,
                                width=self.__node_width,
                                height=self.__node_height,
                                representation=NodeRepresentation.GROUP.value,
                            )

                        else:
                            raise RuntimeError(
                                f"Group {groups_edge_mapping[destination.target].path} is not in the graph"
                            )
                        edge_name = groups_edge_mapping[destination.target].resource_id

                    else:
                        edge_name = destination.target

                    self.graph.edge(
                        layout_element.resource_id,
                        edge_name,
                        pos=position,
                        representation=destination.representation.value,
                        resource_id=f"{layout_element.resource_id}_{edge_name}",
                    )

    def get_pos_parameter_from_definition(
        self, resource_mapping: dict[str, D], resource_id: str
    ):
        position = resource_mapping.get(resource_id)
        if position:
            pos = f"{position.x},{position.y}"
            return pos
        else:
            return None

    def as_dict(self):
        return json.loads(self.graph.pipe(format="json"))
