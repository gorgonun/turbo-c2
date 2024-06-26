import axios from "axios";
import { MetricsAggregated } from "../domain/metrics-aggregated";

export async function getAggregatedMetricByQueue(queueName: string): Promise<string[]> {
  return (await axios.get(`http://localhost:8000/api/v1/metrics/queues/${queueName}/aggregated`)).data;
}

export async function getAggregatedMetricByGroup(groupName: string): Promise<MetricsAggregated> {
  return (await axios.get(`http://localhost:8000/api/v1/metrics/groups/${groupName}/aggregated`)).data;
}
