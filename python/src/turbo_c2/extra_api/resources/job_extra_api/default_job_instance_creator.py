from dataclasses import asdict
from typing import Any

from pydantic import BaseModel
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition
from turbo_c2.interfaces.job_instance_creator import JobInstanceCreator
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.queues.queue_reference import QueueReference


class DefaultJobInstanceCreator(JobInstanceCreator):
    async def create(self, definition: JobInstanceData, meta: dict[str, Any]):
        def get_reference_from_queue_reference_dict(queue_reference: dict[str, Any] | str) -> QueueReference:
            return QueueReference(**queue_reference) if isinstance(queue_reference, dict) else QueueReference(queue_reference)
        
        def to_job_instance(job_instance_data: dict[str, Any]):
            input_queue = job_instance_data.pop("input_queue_reference", None)
            instance_resource_id = job_instance_data.pop("instance_resource_id", None)
            job_instance_input_queue = (
                get_reference_from_queue_reference_dict(input_queue)
                if input_queue
                else None
            )
            job_instance_extra_queues = [
                get_reference_from_queue_reference_dict(x)
                for x in job_instance_data.pop("extra_queues_references", [])
            ]
            job_instance_output_queues = [
                get_reference_from_queue_reference_dict(x)
                for x in job_instance_data.pop("output_queues_references", [])
            ]
            return JobInstance(
                    **job_instance_data,
                    **({"instance_resource_id": instance_resource_id} if instance_resource_id else {}),
                    input_queue_reference=job_instance_input_queue,
                    extra_queues_references=job_instance_extra_queues,
                    output_queues_references=job_instance_output_queues,
                )
                
        def get_job_instance_by_replication_mode(job_instance_data: dict[str, Any]):
            if (
                job_instance_data["replication_mode"]
                == RemoteJobReplicaMode.MANUAL_SETTING
            ):
                return [to_job_instance({**job_instance_data, "job_definition": job_definition})]

            job_instance_data.pop("instance_resource_id", None)

            return [
                to_job_instance(
                    {**job_instance_data, "input_queue_reference": input_queue, "job_definition": job_definition, "replication_mode": RemoteJobReplicaMode.MANUAL_SETTING},
                )
                for input_queue in job_instance_data["extra_queues_references"]
            ]

        # Job controller needs to be indexed by instance id

        job_definition: DynamicJobDefinition = await self.central_api.execute(
            JobDefinitionCrud.get(definition.job_definition_id)
        )

        if not job_definition:
            raise ValueError(
                f"Job definition {definition.job_definition_id} does not exist"
            )

        if job_definition.spec and job_definition.spec.parameters:
            if not definition.parameters:
                raise ValueError(
                    f"Job definition {definition.job_definition_id} has parameters, but none were provided"
                )

            if not isinstance(definition.parameters, job_definition.spec.parameters):
                raise ValueError(
                    f"Job definition {definition.job_definition_id} has parameters, but the provided parameters are not of the correct type"
                )

        if isinstance(definition, BaseModel):
            instance_data = definition.model_dump()
        else:
            instance_data = asdict(definition)

        instance_data.pop("job_definition_id")

        result = get_job_instance_by_replication_mode(instance_data)
        return result
