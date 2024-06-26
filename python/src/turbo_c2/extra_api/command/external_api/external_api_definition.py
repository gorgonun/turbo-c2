from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.command.external_api.external_api_enum import ExternalApiEnum
from turbo_c2.interfaces.external_api import ExternalApi


class ExternalApiDefinition(DefinitionCommand[ExternalApi, ExternalApi]):
    api_identifier = ExternalApiEnum.API_ID.value
    api_path = "external_apis/external_api"
