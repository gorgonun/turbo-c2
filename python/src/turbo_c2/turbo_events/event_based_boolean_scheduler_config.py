from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventBasedBooleanSchedulerConfig():
    profile: str
    mode: str
    default_queue_name: str
    default_queue_meta: dict[str, Any]


@dataclass
class DefaultEventBasedBooleanSchedulerConfig(EventBasedBooleanSchedulerConfig):
    profile: str = "default"
    mode: str = "remote"
    default_queue_name: str = "EventBasedBooleanSchedulerDefaultQueue"
    default_queue_meta: dict[str, Any] = field(default_factory=lambda: {})
