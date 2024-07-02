import abc
import asyncio
from typing import Any
from turbo_c2.helpers.event_utils import EventUtils
from turbo_c2.jobs.job import Job


class ManagedJob(Job, abc.ABC):
    def __init__(self, name: str, single_run: bool, wait_time: int, finished_event: asyncio.Event | None = None, pause_event: asyncio.Event | None = None) -> None:
        self.__single_run = single_run
        self.__wait_time = wait_time
        self.__finished_event = finished_event
        self.__running_event = pause_event
        super().__init__(name=name)

    @property
    def single_run(self) -> bool:
        return self.__single_run
    
    @property
    def wait_time(self) -> int:
        return self.__wait_time

    @property
    def finished_event(self) -> asyncio.Event:
        if not self.__finished_event:
            self.__finished_event = asyncio.Event()
        return self.__finished_event
    
    @property
    def running_event(self) -> asyncio.Event:
        if not self.__running_event:
            self.__running_event = asyncio.Event()
            self.__running_event.set()
        return self.__running_event
    
    async def pause(self):
        self.running_event.clear()

    async def resume(self):
        self.running_event.set()

    @abc.abstractmethod
    async def can_run(self):
        pass

    @abc.abstractmethod
    async def run_defined_job(self):
        pass

    async def run(self):
        try:
            return await self.managed_run()
        except Exception as exception: # pylint: disable=broad-except
            print("Exception", exception)
            await self.on_job_execution_exception(exception)
            raise

    async def managed_run(self):
        self.logger.debug(f"ManagedJob - run - single_run: {self.__single_run}")
        if self.__single_run:
            await self.run_defined_job()
            return self

        while await self.can_run():
            if not self.running_event.is_set():
                self.logger.debug("ManagedJob - run - pause_event is set")
                await self.running_event.wait()

            await self.run_defined_job()
            
            await EventUtils.safe_wait_for(self.finished_event.wait(), self.__wait_time)
            if self.finished_event.is_set():
                self.logger.debug("ManagedJob - run - finished_event is set")
                await self.graceful_shutdown()
                break

    async def graceful_shutdown(self):
        pass

    async def on_job_execution_exception(self, exception: Exception):
        pass

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        return await self.run_defined_job(*args, **kwds)
