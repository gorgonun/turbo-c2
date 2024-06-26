import json
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.helpers.serde.job_instance_serde import JobInstanceSerDe
from turbo_c2.jobs.job_instance import JobInstance


class JobGroupWithInstancesSerDe:
    @staticmethod
    def to_dict(job_group_with_instances: JobGroupWithInstances) -> dict:
        return {
            "resource_id": job_group_with_instances.resource_id,
            "name": job_group_with_instances.name,
            "description": job_group_with_instances.description,
            "path": job_group_with_instances.path,
            "job_instances": [
                JobInstanceSerDe.to_dict(job_instance)
                for job_instance in job_group_with_instances.job_instances
            ],
        }

    @staticmethod
    def serialize(job_instance: JobInstance) -> str:
        return json.dumps(JobInstanceSerDe.to_dict(job_instance))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
