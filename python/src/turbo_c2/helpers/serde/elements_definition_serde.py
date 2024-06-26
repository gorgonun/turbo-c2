import json
from typing import Any
from turbo_c2.domain.gui.layout_grid_response import LayoutGridResponse
from turbo_c2.helpers.serde.job_group_serde import JobGroupWithInstancesSerDe
from turbo_c2.helpers.serde.layout_definition_serde import LayoutDefinitionSerDe


class LayoutGridResponseSerDe:
    @staticmethod
    def to_dict(layout_grid_response: LayoutGridResponse, instances_data: dict[str, Any]) -> dict:
        return {
            "group": JobGroupWithInstancesSerDe.to_dict(layout_grid_response.group),
            "subgroups": [JobGroupWithInstancesSerDe.to_dict(x) for x in layout_grid_response.subgroups],
            "layout_definition": LayoutDefinitionSerDe.to_dict(layout_grid_response.layout_definition),
            "instances_data": instances_data
        }

    @staticmethod
    def serialize(layout_grid_response: LayoutGridResponse, instances_data: dict[str, Any]) -> str:
        return json.dumps(LayoutGridResponseSerDe.to_dict(layout_grid_response, instances_data))

    # @staticmethod
    # def deserialize(job_instance_json: str) -> JobInstance:
    #     return json.loads(job_instance_json, cls=JobInstanceDecoder)
