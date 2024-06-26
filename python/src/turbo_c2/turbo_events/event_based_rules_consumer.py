import asyncio
from collections import deque
import datetime
import time
from turbo_c2.decorators.job import job
from turbo_c2.jobs.job_output import JobOutput
from turbo_c2.turbo_events.event_store.event_store_controller import (
    EventStoreController,
)
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.jobs.job_factory import JobFactory
from turbo_c2.jobs.dynamic_job.dynamic_job_helper_api import DynamicJobHelperApi
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.queues.queue_definition import QueueDefinition


class EventBasedRulesConsumerJobFactory(JobFactory):
    def __init__(
        self,
        event_store_controller: EventStoreController,
        queues_definition: list[QueueDefinition],
        output_queue: QueueDefinition,
    ) -> None:
        self.__queues_definition = queues_definition
        self.__event_store_controller = event_store_controller
        self.__output_queue = output_queue

    def get_job_constructor(self, replicas: int = 1, safe: bool = False):
        @job(
            extra_queues_references=[
                queue_definition.name for queue_definition in self.__queues_definition
            ],
            output_queues_references=[self.__output_queue.name],
            event_store=self.__event_store_controller,
            representation=NodeRepresentation.ACTION,
            replicas=replicas,
            safe=safe,
        )
        async def consumer(
            content: Event, event_store: EventStoreController, api: DynamicJobHelperApi, safe
        ):
            # before_start = time.perf_counter()

            # before_put = time.perf_counter()
            # api.logger.info("running event consumer")

            # before_get_session = time.perf_counter()
            # session = await event_store.put_event(content)

            with api.buffer_context() as buffer:
                contents = [content]
                for item in buffer:
                    if isinstance(item, JobOutput):
                        contents.append(item.content)
                    else:
                        contents.append(item)

                # FIXME: Not safe if NOT predicate is used on handler expression
                before_put = time.perf_counter()
                req = await event_store.put_events(contents, acquire_lock=False)
                after_put = time.perf_counter()
                api.logger.debug(f"put event took {after_put - before_put} seconds")
                await event_store.is_request_finished(req)

            # Locked
            # while not session:
            #     session = await event_store.put_event(content, acquire_lock=False)
            #     await asyncio.sleep(0.01)

            # after_get_session = time.perf_counter()
            # api.logger.info(f"get session took {after_get_session - before_get_session} seconds")

            # api.logger.info("put event on event store")
            # after_put = time.perf_counter()
            # api.logger.info(f"put event took {after_put - before_put} seconds")


            # after_start = time.perf_counter()
            # api.logger.info(f"consumer took {after_start - before_start} seconds")
            
            return [JobOutput(content=data, content_parameters={"session": None}) for data in contents]

        return consumer
