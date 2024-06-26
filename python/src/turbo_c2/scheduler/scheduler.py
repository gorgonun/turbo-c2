import abc

from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.queue_api import QueueApi


class Scheduler(abc.ABC):
    def __init__(self, jobs: list[JobApi], queue: QueueApi):
        self.__jobs = jobs
        self.__queue = queue

    @property
    def jobs(self):
        return self.__jobs
    
    @property
    def queue(self):
        return self.__queue

    @abc.abstractmethod
    async def start(self):
        pass
