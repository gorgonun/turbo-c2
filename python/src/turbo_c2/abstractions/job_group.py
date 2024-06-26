from dataclasses import dataclass, field
from turbo_c2.helpers.name_utils import generate_resource_id

from turbo_c2.mixin.has_id import HasId


@dataclass
class JobGroup(HasId):
    name: str
    path: str
    description: str | None
    # TODO: Is it necessary, as usually the path could be it's id
    group_resource_id: str = field(default_factory=lambda: generate_resource_id("JobGroup"))
    job_instances: list[str] = field(default_factory=list)
    read_only: bool = False
    meta: dict[str, str] = field(default_factory=dict)

    @property
    def resource_id(self):
        return self.group_resource_id
