from typing import Callable
from turbo_c2.globals.ebf_global import get_scheduler_globals

from turbo_c2.queues.queue_definition import QueueDefinition


def queue(for_types: list[type] | None = None):
    def wrapper(func: Callable[[], QueueDefinition]):
        definition = func()
        definition.add_alias(*(for_types or []))
        get_scheduler_globals().add_queue(definition)
        return definition
    return wrapper
