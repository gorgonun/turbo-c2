from __future__ import annotations
import asyncio
from typing import Any
from turbo_c2.jobs.managed_job_with_queue_evaluation import ManagedJobWithQueueEvaluation
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces.queue_api import QueueApi


class RemoteJob(ManagedJobWithQueueEvaluation):
    def __init__(
        self,
        queues_reference: list[QueueDefinition],
        name: str,
        wait_time=1,
        single_run=False,
        queues_reference_mapping: dict[QueueReference, QueueApi] | None = None,
        finished_event: asyncio.Event | None = None,
        pause_event: asyncio.Event | None = None,
    ) -> None:
        super().__init__(
            name=name,
            wait_time=wait_time,
            single_run=single_run,
            queues_reference=queues_reference,
            queues_reference_mapping=queues_reference_mapping,
            finished_event=finished_event,
            pause_event=pause_event,
        )

    async def can_run(self) -> bool:
        return True

    def __reduce__(self) -> str | tuple[Any, ...]:
        deserializer = RemoteJob.create
        serialized_data = (
            self.queue_identificators,
            self.name,
            self.wait_time,
            self.single_run,
            self.evaluated_queues,
            self.finished_event.is_set() if self.finished_event else None,
        )
        return deserializer, serialized_data

    @classmethod
    def create(
        cls,
        queues_reference: list[QueueDefinition],
        name: str,
        wait_time=1,
        single_run=False,
        evaluated_queues: list[QueueApi] | None = None,
        finished: bool | None = None,
    ):
        event = asyncio.Event() if finished is not None else None

        if finished:
            event.set()

        return cls(
            queues_reference,
            name,
            wait_time,
            single_run,
            evaluated_queues,
            finished_event=event,
        )
