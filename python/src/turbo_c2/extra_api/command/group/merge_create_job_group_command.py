from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.extra_api.command.group.group_enum import GroupEnum

from turbo_c2.interfaces.command import Command


@dataclass
class MergeCreateJobGroupCommand(Command[Tuple[str, JobGroup], None]):
    group_path: str
    group: JobGroup
    api_identifier: ClassVar[str] = GroupEnum.API_ID.value
    api_path: ClassVar[str] = "groups/merge_create"
