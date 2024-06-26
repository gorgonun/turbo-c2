import abc
from typing import TypeVar
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.interfaces.queue_api import QueueApi


J = TypeVar("J", bound=JobInstance)


class DefaultJobController(JobController[J], abc.ABC):
    def __init__(self, job_instance: J, start_number_of_replicas: int = 1) -> None:
        self.__job_instance = job_instance
        self.start_number_of_replicas = start_number_of_replicas
        self.__replicas = 0

    @property
    def job_instance(self) -> J:
        return self.__job_instance

    @property
    def replicas(self):
        return self.__replicas
    
    @replicas.setter
    def replicas(self, value):
        self.__replicas = value

    async def get_replicas(self):
        return self.__replicas
    
    async def get_job_instance(self) -> J:
        return self.job_instance

    async def start(self, replicas: int | None = None):
        self.__replicas = replicas or 0

    def get_name(self):
        return self.job_instance.name

    def get_job(self):
        return self.job_instance

    # FIXME: Implement this for all replicas
    async def graceful_shutdown(self):
        return self.job_instance.graceful_shutdown()

    # FIXME: Implement this for local jobs
    async def finished(self):
        raise NotImplementedError()

    async def successful(self):
        raise NotImplementedError()

    async def failed(self):
        raise NotImplementedError()

    async def exceptions(self):
        raise NotImplementedError()

    async def scale(self, replicas: int):
        self.__replicas += replicas

    async def wait_finished(self):
        raise NotImplementedError()

    async def add_central_api(self, central_api: DefaultCentralApi):
        raise NotImplementedError()

    async def evaluate_queues(self, queues: dict[QueueReference, QueueApi]):
        return await self.job_instance.evaluate_queues(queues)
    
    async def pause(self):
        raise NotImplementedError()
    
    async def resume(self):
        raise NotImplementedError()
    
    async def get_state(self):
        raise NotImplementedError()
