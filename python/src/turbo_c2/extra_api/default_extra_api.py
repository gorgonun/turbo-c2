from typing import Any, Callable, Type, TypeVar, cast
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.helpers.command import command_path_from_command
from turbo_c2.interfaces.command import Command

from turbo_c2.exceptions.exceptions import RouteNotFoundException
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.interfaces.extra_api import ExtraApi


T = TypeVar("T")
U = TypeVar("U")


class DefaultExtraApi(ExtraApi, NeedsCentralApi):
    def __init__(self, command_mapping: list[tuple[Type[Command] | CommandPath, Callable[..., Any]]], api_id: str, central_api: CentralApiApi | None = None) -> None:
        self.__routes = self.create_execution_route(command_mapping)
        self.__logger = TurboLogger("ExtraApi")
        self.__api_id = api_id
        super().__init__(central_api)

    @property
    def routes(self):
        return self.__routes
    
    @property
    def paths(self):
        return self.get_all_paths()
    
    @property
    def logger(self):
        return self.__logger
    
    @property
    def api_id(self):
        return self.__api_id

    def get_all_paths(self):
        def get_paths(cursor, path: list[str]) -> list[str]:
            if isinstance(cursor, dict):
                return [paths for key in cursor.keys() for paths in get_paths(cursor[key], [*path, key])]
            return [path]
        
        return get_paths(self.routes, [])
    
    def create_execution_route(self, command_mapping: list[tuple[Type[Command] | CommandPath, Callable[..., Any]]]):
        routes = {}
        for maybe_command, function in command_mapping:
            if isinstance(maybe_command, CommandPath):
                command = maybe_command
            else:
                command = command_path_from_command(maybe_command)
                # print(command, command.api_id, command.api_path_list, command.command_id)
            routes.setdefault(command.api_id, {})

            cursor = routes[command.api_id]
            api_path_list = command.api_path_list

            for path in api_path_list:
                cursor = cursor.setdefault(path, {})
            
            cursor[command.command_id] = function

        return routes
    
    def get_routes(self):
        return self.routes
    
    def set_route(self, path: str, function: Callable[..., Any]):
        api_path_list = path.split("/")
        cursor = self.routes

        for path in api_path_list[:-1]:
            cursor = cursor.setdefault(path, {})
        
        cursor[api_path_list[-1]] = function

    async def execute(self, command: Command[T, U], *args, **kwargs) -> U:
        api_path_list = [command.api_identifier, *command.api_path.split("/")]
        cursor = self.routes

        self.logger.debug(f"Executing {'/'.join(api_path_list)}")

        for path in api_path_list[:-1]:
            cursor = cursor.get(path)
            if not cursor:
                raise RouteNotFoundException(f"Path {api_path_list} not found")

        return await cast(U, cursor[api_path_list[-1]](command, *args, **kwargs))
