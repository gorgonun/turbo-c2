from dataclasses import dataclass


@dataclass
class ApiReference:
    api_id: str
    api_path: str

    @property
    def complete_id_path(self):
        return [self.api_id, *self.api_path.split("/")]
    
    @property
    def complete_id(self):
        return "/".join([self.api_id, self.api_path])
