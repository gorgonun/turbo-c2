from collections.abc import Hashable
from dataclasses import dataclass
import os
from typing import Tuple
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.helpers.generics import API, DEFINITION
from turbo_c2.interfaces.dynamic_command import DynamicCommand
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData


@dataclass
class CreateInstanceByDefinitionIdCommand(
    DynamicCommand[Tuple[DEFINITION, Hashable, Hashable, bool], list[API]]
):
    job_instance_data: JobInstanceData
    creator_id: Hashable | None = None
    fail_if_exists: bool = True
    api_identifier: str
    api_path: str
    indexes: list[str] | None = None


class JobInstanceCrud(CrudCommand[JobInstanceData, JobInstance]):
    api_identifier = JobEnum.API_ID.value
    api_path = "job_instances/instance"
    indexes = [
        "job_definition_id",
        "input_queue_reference",
        "extra_queues_references",
        "output_queues_references",
        "derivated_id"
    ]

    @classmethod
    def create(
        cls,
        job_instance_data: JobInstanceData,
        creator_id: Hashable | None = None,
        fail_if_exists: bool = True,
    ) -> DynamicCommand[DEFINITION, API]:
        return CreateInstanceByDefinitionIdCommand(
            job_instance_data=job_instance_data,
            creator_id=creator_id,
            fail_if_exists=fail_if_exists,
            api_identifier=cls.api_identifier,
            api_path=os.path.join(cls.api_path, "create"),
            indexes=cls.indexes,
        )
