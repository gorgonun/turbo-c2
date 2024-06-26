from typing import Any
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


class DefaultJobApi(JobApi):
    def __init__(self, job_controller: JobController) -> None:
        self.__job_controller = job_controller

    @property
    def job_controller(self) -> JobController:
        return self.__job_controller

    async def start(self, replicas: int | None = None):
        return await self.__job_controller.start(replicas)

    async def get_name(self):
        return await self.__job_controller.get_name()

    async def get_job(self):
        return await self.__job_controller.get_job()

    async def graceful_shutdown(self):
        return await self.__job_controller.graceful_shutdown()

    async def finished(self):
        return await self.__job_controller.finished()

    async def successful(self):
        return await self.__job_controller.successful()

    async def failed(self):
        return await self.__job_controller.failed()

    async def exceptions(self):
        return await self.__job_controller.exceptions()

    async def scale(self, replicas: int):
        return await self.__job_controller.scale(replicas)

    async def wait_finished(self):
        return await self.__job_controller.wait_finished()

    async def add_central_api(self, central_api: DefaultCentralApi):
        return await self.__job_controller.add_central_api(central_api)

    async def evaluate_queues(self, queues: dict[QueueReference, QueueApi]):
        return await self.__job_controller.evaluate_queues(queues)
    
    def __reduce__(self) -> str | tuple[Any, ...]:
        return self.create, (self.__job_controller,)
    
    @classmethod
    def create(cls, job_controller: JobController) -> JobApi:
        return cls(job_controller)
