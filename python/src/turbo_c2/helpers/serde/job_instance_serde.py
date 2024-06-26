import json
from turbo_c2.helpers.serde.job_parameter_serde import JobParameterSerde
from turbo_c2.jobs.job_instance import JobInstance


class JobInstanceSerDe:
    @staticmethod
    def to_dict(job_instance: JobInstance) -> dict:
        return {
            "resource_id": job_instance.resource_id,
            "name": job_instance.name,
            "job_definition": job_instance.job_definition.resource_id,
            "replicas": job_instance.replicas,
            "replication_mode": job_instance.replication_mode.value,
            "read_only": job_instance.read_only,
            "group_path": job_instance.group_path,
            "input_queue_reference": job_instance.input_queue_reference,
            "extra_queues_references": job_instance.extra_queues_references,
            "output_queues_references": job_instance.output_queues_references,
            "parameters": job_instance.parameters if isinstance(job_instance.parameters, dict) else JobParameterSerde.to_dict(job_instance.parameters),
            "derivated_id": job_instance.derivated_id,
        }

    @staticmethod
    def serialize(job_instance: JobInstance) -> str:
        return json.dumps(JobInstanceSerDe.to_dict(job_instance))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
