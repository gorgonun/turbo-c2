from dataclasses import dataclass
from typing import Any
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.config.config import Config
from turbo_c2.queues.queue_reference import QueueReference

from turbo_c2.globals.scheduler_globals import SchedulerGlobals
from turbo_c2.interfaces.queue_api import QueueApi


@dataclass
class LazySchedulerParameters:
    config: Config
    central_api: DefaultCentralApi
    ebf_globals: SchedulerGlobals
    remote_objects: dict[str, Any]
    queues: dict[QueueReference, QueueApi]
