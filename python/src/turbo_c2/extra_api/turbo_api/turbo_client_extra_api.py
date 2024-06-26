import functools
from typing import Any
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.client.client_definition import ClientDefinition
from turbo_c2.extra_api.command.client.client_enum import ClientEnum
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi


class ClientExtraApi(DefaultExtraApiWithSubApis):
    def __init__(self, central_api: CentralApiApi | None = None) -> None:
        self.__apis = [
            DefinitionResourceApi(ClientDefinition)
        ]
        super().__init__(
            self.__apis,
            [
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            ClientEnum.API_ID.value,
            central_api=central_api
        )
    
    def __reduce__(self) -> str | tuple[Any, ...]:
        return functools.partial(ClientExtraApi, central_api=self.central_api), tuple()
