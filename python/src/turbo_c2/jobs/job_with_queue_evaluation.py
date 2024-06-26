from turbo_c2.jobs.job import Job
from turbo_c2.mixin.needs_queue_evaluation import NeedsQueueEvaluation
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


class JobWithQueueEvaluation(Job, NeedsQueueEvaluation):
    def __init__(self, name: str, queues_reference: list[QueueReference] | None=None, queues_reference_mapping: dict[QueueReference, QueueApi] | None=None) -> None:
        super().__init__(name)
        NeedsQueueEvaluation.__init__(self, queues_reference, queues_reference_mapping)
