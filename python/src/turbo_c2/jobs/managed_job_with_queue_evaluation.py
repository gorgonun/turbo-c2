import asyncio
from turbo_c2.jobs.job_with_queue_evaluation import JobWithQueueEvaluation
from turbo_c2.jobs.managed_job import ManagedJob
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


class ManagedJobWithQueueEvaluation(ManagedJob, JobWithQueueEvaluation):
    def __init__(
        self,
        name: str,
        single_run: bool,
        wait_time: int,
        queues_reference: list[str] | None = None,
        queues_reference_mapping: dict[QueueReference, QueueApi] | None = None,
        finished_event: asyncio.Event | None = None,
        pause_event: asyncio.Event | None = None,
    ) -> None:
        super().__init__(name, single_run, wait_time, finished_event=finished_event, pause_event=pause_event)
        JobWithQueueEvaluation.__init__(self, name, queues_reference, queues_reference_mapping)
