from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.group.group_enum import GroupEnum


class GroupCrud(CrudCommand[JobGroup, JobGroup]):
    api_identifier = GroupEnum.API_ID.value
    api_path = "groups"
    indexes = ["job_instances"]
