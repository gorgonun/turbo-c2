import { QueueReference } from "./queue-reference";

export enum RemoteJobReplicaMode {
    MANUAL_SETTING = "manual_setting",
    FOLLOW_QUEUE = "follow_queue",
}

export type JobInstance<Parameter = object> = {
    job_definition: string;
    replicas: number
    replication_mode: RemoteJobReplicaMode
    read_only: boolean;
    group_path: string
    resource_id: string;
    input_queue_reference: QueueReference | null
    extra_queues_references: QueueReference[];
    output_queues_references: QueueReference[];
    parameters: Parameter | null;
    name: string | null;
}
