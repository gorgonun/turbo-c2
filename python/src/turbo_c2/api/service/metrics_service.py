import asyncio
from turbo_c2.clients.prometheus.prometheus_http_client import PrometheusHttpClient
from turbo_c2.extra_api.command.client.client_definition import ClientDefinition

from turbo_c2.extra_api.command.group.get_job_group_with_instances_command import (
    GetJobGroupWithInstancesCommand,
)
from turbo_c2.interfaces.api import Api
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class MetricsService(Api, NeedsCentralApi):
    async def get_aggregated_metrics_by_group(
        self, group_path: str, time: str | None = None
    ):
        async def get_metric(
            prometheus_client: PrometheusHttpClient,
            template: str,
            resource_id: str,
            aggregated_type: str,
            **kwargs,
        ):

            result = (
                resource_id,
                aggregated_type,
                prometheus_client.query_instant(
                    query=template.format(**kwargs),
                    time=time,
                    timeout=10,
                ),
            )
            
            return result

        prometheus_client: PrometheusHttpClient = await self.central_api.execute(
            ClientDefinition.get(PrometheusHttpClient)
        )

        group_with_instances = await self.central_api.execute(
            GetJobGroupWithInstancesCommand(group_path)
        )

        aggregated_metrics = {}

        # runtime_job_query_template = (
        #     'sum(ebf_job_runtime_seconds_created{{job_id="{job_id}"}})'
        # )
        input_job_query_template = 'sum(tc2_input_counter_total{{job_id="{job_id}"}})'
        output_job_query_template = 'sum(tc2_output_counter_total{{job_id="{job_id}"}})'
        replicas_job_query_template = 'sum(tc2_job_replicas_counter{{job_id="{job_id}"}})'

        queue_query_template = 'sum(tc2_queue_content{{queue_name="{queue_name}"}})'

        results = await asyncio.gather(
            # *[
            #     get_metric(
            #         prometheus_client,
            #         runtime_job_query_template,
            #         instance.resource_id,
            #         "runtime",
            #         job_id=instance.resource_id,
            #     )
            #     for instance in group_with_instances.job_instances
            # ],
            *[
                get_metric(
                    prometheus_client,
                    input_job_query_template,
                    instance.resource_id,
                    "input",
                    job_id=instance.resource_id,
                )
                for instance in group_with_instances.job_instances
            ],
            *[
                get_metric(
                    prometheus_client,
                    output_job_query_template,
                    instance.resource_id,
                    "output",
                    job_id=instance.resource_id,
                )
                for instance in group_with_instances.job_instances
            ],
            *[
                get_metric(
                    prometheus_client,
                    replicas_job_query_template,
                    instance.resource_id,
                    "replicas",
                    job_id=instance.resource_id,
                )
                for instance in group_with_instances.job_instances
            ],
            *[
                get_metric(
                    prometheus_client,
                    queue_query_template,
                    instance.input_queue_reference.identifier,
                    "input",
                    queue_name=instance.input_queue_reference.identifier,
                )
                for instance in group_with_instances.job_instances
                if instance.input_queue_reference
            ],
            *[
                get_metric(
                    prometheus_client,
                    queue_query_template,
                    output_queues_reference.identifier,
                    "input",
                    queue_name=output_queues_reference.identifier,
                )
                for instance in group_with_instances.job_instances
                for output_queues_reference in instance.output_queues_references
            ],
            *[
                get_metric(
                    prometheus_client,
                    queue_query_template,
                    extra_queues_reference.identifier,
                    "input",
                    queue_name=extra_queues_reference.identifier,
                )
                for instance in group_with_instances.job_instances
                for extra_queues_reference in instance.extra_queues_references
            ],
        )

        for resource_id, aggregated_type, prom_result in results:
            if prom_result.get("status") == "success":
                result_data = prom_result.get("data", {}).get("result", [])
                if result_data and len(result_data) == 1:
                    aggregated_metrics.setdefault(resource_id, {}).setdefault(
                        aggregated_type, result_data[0].get("value", [])
                    )

        return aggregated_metrics

    async def get_aggregated_metrics_by_queue(
        self, queue_name: str, time: str | None = None
    ):
        prometheus_client: PrometheusHttpClient = await self.central_api.execute(
            ClientDefinition.get(PrometheusHttpClient)
        )

        data = prometheus_client.query_instant(
            query=f'sum(tc2_queue_content{{queue_name="{queue_name}"}})',
            time=time,
            timeout=10,
        )

        if data.get("status") == "success":
            result = data.get("data", {}).get("result", [])
            if result and len(result) == 1:
                return result[0].get("value", [])

            return data.get("data", {}).get("result")
