import { JobGroupWithInstances } from "./job-group-with-instances";
import { LayoutDefinition } from "./layout-definition";

export type LayoutGrid = {
  group: JobGroupWithInstances;
  subgroups: Record<string, JobGroupWithInstances>;
  layout_definition: LayoutDefinition;
  instances_data: { [instanceId: string]: { state: "started" | "paused" } };
};
