from dataclasses import dataclass

from turbo_c2.extra_api.command.api_reference import ApiReference


@dataclass
class CommandPath:
    api_id: str
    api_path: str
    command_id: str

    @property
    def complete_path_list(self):
        return [self.api_id, *self.api_path_list, self.command_id]

    @property
    def api_path_list(self):
        return self.api_path.split("/")

    @property
    def api_reference(self):
        return ApiReference(api_id=self.api_id, api_path=self.api_path)
