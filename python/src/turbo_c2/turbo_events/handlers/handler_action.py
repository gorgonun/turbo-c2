from dataclasses import dataclass
from typing import Callable

from turbo_c2.turbo_events.events.event import Event


@dataclass
class HandlerAction:
    run_function: Callable[[list[Event]], None]
    output_queues: list[str]
