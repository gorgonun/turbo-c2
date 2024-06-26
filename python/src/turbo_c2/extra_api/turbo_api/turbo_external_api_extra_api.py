import functools
from typing import Any
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.external_api.external_api_definition import ExternalApiDefinition
from turbo_c2.extra_api.command.external_api.external_api_enum import ExternalApiEnum
from turbo_c2.extra_api.command.external_api.get_external_apis_mapping_command import GetExternalApisMappingCommand
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.interfaces.external_api import ExternalApi


class ExternalApiExtraApi(DefaultExtraApiWithSubApis):
    def __init__(self, central_api: CentralApiApi | None = None) -> None:
        self.__apis = [
            DefinitionResourceApi(ExternalApiDefinition)
        ]

        super().__init__(
            self.__apis,
            [
                (GetExternalApisMappingCommand, self.get_external_apis_mapping),
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            ExternalApiEnum.API_ID.value,
            central_api=central_api
        )
    
    async def get_external_apis_mapping(self, _: GetExternalApisMappingCommand) -> dict[str, ExternalApi]:
        external_apis: list[ExternalApi] = await self.central_api.execute(ExternalApiDefinition.list())
        mapping = {api.api_identifier: api for api in external_apis}
        return mapping

    def __reduce__(self) -> str | tuple[Any, ...]:
        return functools.partial(ExternalApiExtraApi, central_api=self.central_api), tuple()
