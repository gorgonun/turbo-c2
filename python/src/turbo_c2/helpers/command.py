from typing import Type
from turbo_c2.extra_api.command.command_path import CommandPath
from turbo_c2.interfaces.command import Command


def command_path_from_command(command: Type[Command]):
    api_path, command_id = command.api_path.rsplit("/", 1)
    return CommandPath(
        api_id=command.api_identifier, api_path=api_path, command_id=command_id
    )
