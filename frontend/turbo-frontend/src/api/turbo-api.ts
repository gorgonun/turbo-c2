import axios from "axios";
import { LayoutGrid } from "../domain/layout-grid";
import { PositionDefinition } from "../domain/layout-definition";
import { JobInstanceDataRequest } from "../domain/job-instance-data-request";

export async function getJobs(): Promise<string[]> {
  return (await axios.get("http://localhost:8000/api/v1/jobs")).data;
}

export async function getJobGroup(path: string): Promise<LayoutGrid> {
  return (await axios.get(`http://localhost:8000/api/v1/groups/${path}`)).data;
}

export async function getDefinitions(): Promise<any[]> {
  return (await axios.get("http://localhost:8000/api/v1/definitions")).data;
}

export async function move_element(layout_id: string, elements: Record<string, { position_definition: Pick<PositionDefinition, 'x' | 'y'>; element_type: string }[]>): Promise<PositionDefinition> {
  return (await axios.put(`http://localhost:8000/api/v1/layouts/${layout_id}/move_elements`, elements)).data;
}

export async function create_job_instance(req: JobInstanceDataRequest): Promise<PositionDefinition> {
  return (await axios.post(`http://localhost:8000/api/v1/job_instances`, req)).data;
}

export async function listJobGroup(srcPath: string): Promise<string[]> {
  return (await axios.get(`http://localhost:8000/api/v1/groups?src_path=${srcPath}`)).data;
}

export async function getMetricsByGroup(groupPath: string): Promise<any> {
  return (await axios.get(`http://localhost:8000/api/v1/metrics/groups/${groupPath}/aggregated`)).data;
}

export async function listQueues(): Promise<string[]> {
  return (await axios.get(`http://localhost:8000/api/v1/queues`)).data;
}

export async function scaleJobInstance(instanceId: string, replicas: number): Promise<PositionDefinition> {
  return (await axios.post(`http://localhost:8000/api/v1/jobs/${instanceId}/scale`, { replicas })).data;
}

export async function pauseJobInstance(instanceId: string): Promise<PositionDefinition> {
  return (await axios.put(`http://localhost:8000/api/v1/jobs/${instanceId}/pause`)).data;
}

export async function resumeJobInstance(instanceId: string): Promise<PositionDefinition> {
  return (await axios.put(`http://localhost:8000/api/v1/jobs/${instanceId}/resume`)).data;
}
