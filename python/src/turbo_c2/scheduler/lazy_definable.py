import abc
from typing import Any
from turbo_c2.scheduler.lazy_scheduler_parameters import LazySchedulerParameters
from turbo_c2.queues.queue_definition import QueueDefinition

from turbo_c2.globals.scheduler_globals import SchedulerDefinitions


class LazyDefinable(abc.ABC):

    def __init__(self, name: str) -> None:
        self.__name = name

    @property
    def name(self):
        return self.__name

    @abc.abstractmethod
    def get_queues(self) -> list[QueueDefinition]:
        raise NotImplementedError("get_queues method not implemented")
    
    @abc.abstractmethod
    def get_remote_objects(self) -> dict[str, Any]:
        raise NotImplementedError("get_remote_objects method not implemented")

    @abc.abstractmethod
    async def setup(self, scheduler_parameters: LazySchedulerParameters, *args, **kwargs) -> SchedulerDefinitions:
        raise NotImplementedError("create method not implemented")
