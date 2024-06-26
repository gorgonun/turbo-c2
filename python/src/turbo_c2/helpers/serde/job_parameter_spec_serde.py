from dataclasses import asdict
import json
from turbo_c2.jobs.job_input_spec import JobInputSpec
from pydantic import TypeAdapter


class JobParameterSpecSerDe:
    @staticmethod
    def to_dict(job_parameter_spec: JobInputSpec) -> dict:
        return {
            "queues": {
                "input_queue": asdict(job_parameter_spec.queues.input_queue) if job_parameter_spec.queues.input_queue else None,
                "extra_queues": asdict(job_parameter_spec.queues.extra_queues) if job_parameter_spec.queues.extra_queues else None,
                "output_queues": asdict(job_parameter_spec.queues.output_queues) if job_parameter_spec.queues.output_queues else None,
            },
            "fields": (
                TypeAdapter(job_parameter_spec.parameters).json_schema()
                if job_parameter_spec.parameters
                else None
            ),
        }

    @staticmethod
    def serialize(job_parameter_spec: JobInputSpec) -> str:
        return json.dumps(JobParameterSpecSerDe.to_dict(job_parameter_spec))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
