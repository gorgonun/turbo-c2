import { JobInstance } from "./job-instance";

export type JobGroupWithInstances = {
    name: string;
    path: string;
    description: string | null;
    resource_id: string;
    job_instances: JobInstance[];
    read_only: boolean;
    meta: object;
}
