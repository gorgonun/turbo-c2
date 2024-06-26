import json
from turbo_c2.helpers.serde.job_parameter_spec_serde import JobParameterSpecSerDe
from turbo_c2.helpers.serde.meta_serde import MetaSerDe
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition


class DynamicJobDefinitionSerDe:
    @staticmethod
    def to_dict(job_definition: DynamicJobDefinition) -> dict:
        return {
            "name": job_definition.name,
            "description": job_definition.description,
            "run_function": job_definition.run_function.__name__,
            "wait_time": job_definition.wait_time,
            "single_run": job_definition.single_run,
            "meta": MetaSerDe.to_dict(job_definition.meta),
            "tuple_result_is_single_value": job_definition.tuple_result_is_single_value,
            "parameters": JobParameterSpecSerDe.to_dict(job_definition.spec),
        }

    @staticmethod
    def serialize(job_definition: DynamicJobDefinition) -> str:
        return json.dumps(DynamicJobDefinitionSerDe.to_dict(job_definition))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
