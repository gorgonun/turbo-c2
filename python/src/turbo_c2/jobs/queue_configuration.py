from dataclasses import dataclass


@dataclass
class QueueConfiguration:
    name: str
    required: bool
    return_type: type | None = None
