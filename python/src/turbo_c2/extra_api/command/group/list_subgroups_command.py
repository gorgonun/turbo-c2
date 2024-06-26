from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.extra_api.command.group.group_enum import GroupEnum

from turbo_c2.interfaces.command import Command


@dataclass
class ListSubgroupsCommand(Command[Tuple[str | None, JobGroup], list[JobGroup]]):
    group_path: str | None
    api_identifier: ClassVar[str] = GroupEnum.API_ID.value
    api_path: ClassVar[str] = "groups/list_subgroups"
