from __future__ import annotations
import abc
from typing import Any

from turbo_c2.helpers.turbo_logger import TurboLogger


class Job(abc.ABC):

    def __init__(self, name: str, logger: TurboLogger | None = None) -> None:
        self.__name = name
        self.__logger = logger or TurboLogger(name)

    @property
    def name(self):
        return self.__name
    
    @property
    def logger(self):
        return self.__logger
    
    def graceful_shutdown(self):
        pass

    @abc.abstractmethod
    async def run(self, *args, **kwds) -> None:
        pass

    @classmethod
    def get_type(cls):
        return cls.__name__
    
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        return await self.run(*args, **kwds)
