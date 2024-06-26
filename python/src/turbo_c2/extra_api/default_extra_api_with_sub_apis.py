import abc
from typing import Any, Callable
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.extra_api.default_extra_api import DefaultExtraApi
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.command import Command
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


class DefaultExtraApiWithSubApis(DefaultExtraApi, abc.ABC):
    def __init__(self, apis: list[NeedsCentralApi], command_mapping: list[tuple[type[Command] | CommandPath, Callable[..., Any]]], api_id: str, central_api: CentralApiApi | None = None) -> None:
        super().__init__(command_mapping, api_id, central_api)
        self.__apis = apis
        if central_api:
            self.add_central_api(central_api)

    @property
    def apis(self) -> list[NeedsCentralApi]:
        return self.__apis

    def add_central_api(self, central_api: CentralApi):
        super().add_central_api(central_api)
        for api in self.apis:
            if isinstance(api, NeedsCentralApi):
                api.add_central_api(central_api)
