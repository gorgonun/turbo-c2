from dataclasses import dataclass
from typing import ClassVar, Tuple
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.interfaces.command import Command


@dataclass
class ManageJobCommand(Command[Tuple[str, int], None]):
    instance_id: str
    instruction: str
    api_identifier: ClassVar[str] = JobEnum.API_ID.value
    api_path: ClassVar[str] = "job/manage"
