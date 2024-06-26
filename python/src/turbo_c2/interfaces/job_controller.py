import abc
from typing import Any, Generic, TypeVar
from turbo_c2.jobs.job_with_queue_evaluation import JobWithQueueEvaluation
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.central_api.default_central_api import DefaultCentralApi


J = TypeVar("J", bound=JobWithQueueEvaluation)


class JobController(Generic[J], abc.ABC):
    @property
    @abc.abstractmethod
    def job_instance(self) -> J:
        pass

    @property
    @abc.abstractmethod
    def replicas(self) -> int:
        pass

    @abc.abstractmethod
    async def get_replicas(self) -> int:
        pass

    @abc.abstractmethod
    async def get_job_instance(self) -> J:
        pass

    @abc.abstractmethod
    async def start(self, replicas: int | None = None) -> None:
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_job(self) -> J:
        pass

    @abc.abstractmethod
    async def graceful_shutdown(self) -> None:
        pass

    @abc.abstractmethod
    async def finished(self) -> bool:
        pass

    @abc.abstractmethod
    async def successful(self) -> bool:
        pass

    @abc.abstractmethod
    async def failed(self) -> bool:
        pass

    @abc.abstractmethod
    async def exceptions(self) -> list[Exception]:
        pass

    @abc.abstractmethod
    async def scale(self, replicas: int) -> None:
        pass

    @abc.abstractmethod
    async def wait_finished(self):
        pass

    @abc.abstractmethod
    async def add_central_api(self, central_api: DefaultCentralApi) -> None:
        pass

    @abc.abstractmethod
    async def evaluate_queues(self, queues: dict[QueueReference, Any]):
        pass

    @abc.abstractmethod
    async def pause(self) -> None:
        pass

    @abc.abstractmethod
    async def resume(self) -> None:
        pass

    @abc.abstractmethod
    async def get_state(self) -> str:
        pass
