import { RemoteJobReplicaMode } from "./job-instance";
import { PositionDefinition } from "./layout-definition";

export type JobInstanceDataRequest = {
    job_definition_id: string;
    replicas: number;
    replication_mode: RemoteJobReplicaMode;
    read_only: boolean;
    group_path: string;
    input_queue_reference: string | null;
    extra_queues_references: string[];
    output_queues_references: string[];
    parameters: object | null;
    name: string | null;
    position_definition?: Pick<PositionDefinition, 'x' | 'y'>;
    layout_id?: string;
}
