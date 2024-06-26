import json

from turbo_c2.abstractions.job_parameter import JobParameter


class JobParameterSerde:
    @staticmethod
    def to_dict(job_parameter: JobParameter | None) -> dict:
        return job_parameter.model_dump(mode="json") if job_parameter else None

    @staticmethod
    def serialize(job_parameter: JobParameter) -> str:
        return json.dumps(JobParameterSerde.to_dict(job_parameter))

    # def deserialize(self, job_parameter_str: str) -> JobParameter:
    #     return JobParameter.from_dict(json.loads(job_parameter_str))
