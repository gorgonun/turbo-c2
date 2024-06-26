from enum import Enum
import json
from typing import Any


class MetaSerDe:
    @staticmethod
    def to_dict(meta: dict[str, Any]) -> dict:
        result = {}

        for key, value in meta.items():
            if isinstance(value, Enum):
                result[key] = value.value

            else:
                result[key] = str(value)

        return result

    @staticmethod
    def serialize(meta: dict[str, Any]) -> str:
        return json.dumps(MetaSerDe.to_dict(meta))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
