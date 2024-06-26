from dataclasses import dataclass
from typing import Any, ClassVar, Hashable, Tuple
from turbo_c2.api.domain.dto.job.job_instance_data_request import MovePositionDefinitionRequest
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.helpers.generics import API, DEFINITION
from turbo_c2.interfaces.command import Command
from turbo_c2.jobs.job_instance_data import JobInstanceData


@dataclass
class CreateExternalJobInstanceCommand(Command[Tuple[DEFINITION, Hashable, Hashable, bool], list[API]]):
    job_instance_data: JobInstanceData
    position_definition: MovePositionDefinitionRequest | None = None
    layout_id: Hashable | None = None
    creator_id: Hashable | None = None
    fail_if_exists: bool = True
    indexes: list[str] | None = None
    api_identifier: ClassVar[str] = JobEnum.API_ID.value
    api_path: ClassVar[str] = "job_instances/create_external_instance"
