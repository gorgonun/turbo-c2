from turbo_c2.domain.gui.external_job_group_definition import ExternalJobGroupDefinition
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.group.group_enum import GroupEnum


class ExternalJobGroupDefinitionResource(CrudCommand[ExternalJobGroupDefinition, ExternalJobGroupDefinition]):
    api_identifier = GroupEnum.API_ID.value
    api_path = "external_job_group_definitions"
    indexes = ["group_path", "name"]
