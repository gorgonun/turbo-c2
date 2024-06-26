from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.extra_api.command.group.group_enum import GroupEnum

from turbo_c2.interfaces.command import Command
from turbo_c2.jobs.job_instance import JobInstance


@dataclass
class AddJobInstanceToGroupCommand(Command[Tuple[str, JobInstance, bool], None]):
    group_path: str
    job_instance: JobInstance
    fail_if_exists: bool = True
    api_identifier: ClassVar[str] = GroupEnum.API_ID.value
    api_path: ClassVar[str] = "groups/add_job_instance"
