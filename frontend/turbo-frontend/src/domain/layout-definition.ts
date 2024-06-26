export enum NodeRepresentation {
    ACTION = "ACTION",
    DECISION = "DECISION",
    GROUP = "GROUP",
}

export enum EdgeRepresentation {
    QUEUE = "QUEUE",
    CONDITION_TRUE = "CONDITION_TRUE",
    CONDITION_FALSE = "CONDITION_FALSE",
    EXECUTION = "EXECUTION",
}

export type HasNodeRepresentation = {
    representation: NodeRepresentation;
}

export type HasEdgeRepresentation = {
    representation: EdgeRepresentation;
}

export type PositionDefinition = {
    resource_id: string;
    x: number;
    y: number;
    width: number;
    height: number;
}

export type JobInstancePositionDefinition = PositionDefinition & HasNodeRepresentation;

export type QueuePositionDefinition = {
    resource_id: string;
    // head, tail
    connections: string[][];
} & HasEdgeRepresentation;

export type GroupPositionDefinition = PositionDefinition;

export type ItemPositionDefinition = PositionDefinition & HasNodeRepresentation & {
    resource_name: string | null;
}

export type WindowDefinition = {
    resource_id: string;
    job_instances: Record<string, JobInstancePositionDefinition>;
    queues: Record<string, QueuePositionDefinition>;
    sub_groups: Record<string, GroupPositionDefinition>;
    items: Record<string, ItemPositionDefinition>;
    external_groups: Record<string, GroupPositionDefinition>;
}

export type LayoutDefinition = {
    resource_id: string;
    window_definition: WindowDefinition;
    meta: object;
}
