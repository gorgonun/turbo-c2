from typing import TypeVar
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_controller import QueueController


T = TypeVar("T", bound=EBFQueue)


class LocalQueueController(QueueController[T]):
    pass
