import abc
from typing import Any, Callable, Type
from turbo_c2.interfaces.command import Command


class ExtraApi(abc.ABC):
    @property
    @abc.abstractmethod
    def routes(self):
        pass

    @property
    @abc.abstractmethod
    def paths(self):
        pass

    @property
    @abc.abstractmethod
    def api_id(self):
        pass

    @abc.abstractmethod
    def get_all_paths(self):
        pass

    @abc.abstractmethod
    def create_execution_route(
        self, command_mapping: list[tuple[Type[Command], Callable[..., Any]]]
    ):
        pass

    @abc.abstractmethod
    def get_routes(self):
        pass

    @abc.abstractmethod
    def set_route(self, path: str, function: Callable[..., Any]):
        pass

    @abc.abstractmethod
    async def execute(self, command: Command, *args, **kwargs):
        pass
