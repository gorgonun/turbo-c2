from dataclasses import dataclass, field
from turbo_c2.helpers.name_utils import generate_resource_id
from turbo_c2.jobs.job_instance import JobInstance

from turbo_c2.mixin.has_id import HasId


@dataclass
class JobGroupWithInstances(HasId):
    name: str
    path: str
    description: str | None
    group_resource_id: str = field(default_factory=lambda: generate_resource_id("JobGroup"))
    job_instances: list[JobInstance] = field(default_factory=list)
    read_only: bool = False
    meta: dict[str, str] = field(default_factory=dict)

    @property
    def resource_id(self):
        return self.group_resource_id
