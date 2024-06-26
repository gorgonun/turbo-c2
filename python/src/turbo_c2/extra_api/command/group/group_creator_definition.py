from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.group.group_enum import GroupEnum


class GroupCreatorDefinition(DefinitionCommand[str, JobGroup]):
    api_identifier = GroupEnum.API_ID.value
    api_path = "group_creators"
