from dataclasses import dataclass
from typing import Any

from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.domain.gui.layout_definition import LayoutDefinition


@dataclass
class LayoutGridResponse:
    group: JobGroupWithInstances
    subgroups: dict[str, JobGroupWithInstances]
    layout_definition: LayoutDefinition
    instance_data: dict[str, Any]
