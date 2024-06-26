from typing import Any
from pydantic import BaseModel
from turbo_c2.jobs.edge_representation import EdgeRepresentation

from turbo_c2.jobs.node_representation import NodeRepresentation


class PositionDefinition(BaseModel):
    resource_id: str
    x: float
    y: float
    width: float
    height: float


class JobInstancePositionDefinition(PositionDefinition):
    representation: NodeRepresentation


class QueuePositionDefinition(BaseModel):
    resource_id: str
    connections: list[tuple[str, str]]
    representation: EdgeRepresentation


class GroupPositionDefinition(PositionDefinition):
    name: str


class ItemPositionDefinition(PositionDefinition):
    resource_name: str | None
    representation: NodeRepresentation


class WindowDefinition(BaseModel):
    resource_id: str
    job_instances: dict[str, JobInstancePositionDefinition]
    queues: dict[str, QueuePositionDefinition]
    sub_groups: dict[str, GroupPositionDefinition]
    items: dict[str, ItemPositionDefinition]
    external_groups: dict[str, GroupPositionDefinition]


class LayoutDefinition(BaseModel):
    resource_id: str
    window_definition: WindowDefinition
    meta: dict[str, Any] = {}


class LayoutGroupDefinition(BaseModel):
    resource_id: str
    group_path: str
    group_definition_ids: list[str]


class LayoutGroupDefinitionWithLayouts(BaseModel):
    resource_id: str
    group_path: str
    group_definitions: dict[str, LayoutDefinition]
