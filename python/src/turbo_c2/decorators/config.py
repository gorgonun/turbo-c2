from collections.abc import Callable

from turbo_c2.domain.scheduler.config import Config, DefaultConfig

from turbo_c2.globals.ebf_global import get_scheduler_globals


def config():
    def wrapper(func: Callable[[Config], Config]):
        get_scheduler_globals().config = func(get_scheduler_globals().config or DefaultConfig())
    return wrapper
