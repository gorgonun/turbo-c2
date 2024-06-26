from dataclasses import dataclass


prefix = "ebf"


@dataclass
class Config:
    central_api_identifier: str
    job_controller_state_machine_identifier: str
    default_group_path: str


@dataclass
class ModeConfig:
    mode: str


@dataclass
class DefaultConfig(Config, ModeConfig):
    central_api_identifier: str = f"{prefix}_central_api"
    job_controller_state_machine_identifier: str = "job_controller_state_machine"
    default_group_path: str = "root"
    mode: str = "remote"
