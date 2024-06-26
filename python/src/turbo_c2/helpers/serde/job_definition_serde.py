import json
from turbo_c2.helpers.serde.meta_serde import MetaSerDe
from turbo_c2.interfaces.job_definition import JobDefinition


class JobDefinitionSerDe:
    @staticmethod
    def to_dict(job_definition: JobDefinition) -> dict:
        return {
            "name": job_definition.name,
            "description": job_definition.description,
            "run_function": job_definition.run_function.__name__,
            "wait_time": job_definition.wait_time,
            "single_run": job_definition.single_run,
            "meta": MetaSerDe.to_dict(job_definition.meta),
        }

    @staticmethod
    def serialize(job_definition: JobDefinition) -> str:
        return json.dumps(JobDefinitionSerDe.to_dict(job_definition))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
