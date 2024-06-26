from dataclasses import dataclass
from typing import ClassVar
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.extra_api.command.group.group_enum import GroupEnum

from turbo_c2.interfaces.command import Command


@dataclass
class GetJobGroupWithInstancesCommand(Command[str, JobGroupWithInstances]):
    group_path: str
    api_identifier: ClassVar[str] = GroupEnum.API_ID.value
    api_path: ClassVar[str] = "groups/get_with_instances"
