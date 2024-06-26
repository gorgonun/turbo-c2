from turbo_c2.extra_api.command.client.client_enum import ClientEnum
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.interfaces.client import Client


class ClientDefinition(DefinitionCommand[Client, Client]):
    api_identifier = ClientEnum.API_ID.value
    api_path = "clients/client"
