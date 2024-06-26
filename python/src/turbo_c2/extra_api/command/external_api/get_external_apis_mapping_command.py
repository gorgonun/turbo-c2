from dataclasses import dataclass
from typing import ClassVar

from turbo_c2.extra_api.command.external_api.external_api_enum import ExternalApiEnum
from turbo_c2.interfaces.command import Command
from turbo_c2.interfaces.extra_api import ExtraApi


@dataclass
class GetExternalApisMappingCommand(Command[None, dict[str, ExtraApi]]):
    api_identifier: ClassVar[str] = ExternalApiEnum.API_ID.value
    api_path: ClassVar[str] = "external_apis/get_external_apis_mapping"
