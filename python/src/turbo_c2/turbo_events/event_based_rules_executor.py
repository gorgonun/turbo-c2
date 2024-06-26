import asyncio
from itertools import chain
import time
from turbo_c2.decorators.job import job
from turbo_c2.jobs.job_output import JobOutput
from turbo_c2.turbo_events.event_store.event_store_controller import (
    EventStoreController,
)
from turbo_c2.jobs.job_factory import JobFactory
from turbo_c2.jobs.dynamic_job.dynamic_job_helper_api import DynamicJobHelperApi
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.turbo_events.event_store.handler_store_controller import (
    HandlerStoreController,
)


class EventBasedRulesExecutorJobFactory(JobFactory):
    def __init__(
        self,
        event_store_controller: EventStoreController,
        handler_store_controller: HandlerStoreController,
        queues_definition: list[QueueDefinition],
    ) -> None:
        self.__queues_definition = queues_definition
        self.__event_store_controller = event_store_controller
        self.__handler_store_controller = handler_store_controller

    def get_job_constructor(self, replicas: int = 1):
        @job(
            extra_queues_references=[
                queue_definition.name for queue_definition in self.__queues_definition
            ],
            event_store=self.__event_store_controller,
            handler_store=self.__handler_store_controller,
            representation=NodeRepresentation.DECISION,
            replicas=replicas,
        )
        async def executor(
            job_output: JobOutput,
            event_store: EventStoreController,
            handler_store: HandlerStoreController,
            api: DynamicJobHelperApi,
        ):
            api.logger.debug("running event executor")
            before_start = time.perf_counter()

            with api.buffer_context() as buffer:
                contents: list[JobOutput] = [*buffer, job_output]

                events_with_session = [
                    (job_output.content_parameters.get("session"), job_output.content)
                    for job_output in contents
                ]

                try:
                    before_handlers = time.perf_counter()
                    results = await handler_store.get_handler_by_last_events(
                        events_with_session
                    )
                    after_handlers = time.perf_counter()
                    api.logger.debug(
                        f"get handlers took {after_handlers - before_handlers} seconds"
                    )

                    before_cache = time.perf_counter()

                    # One execution by last event. All executed events will have same event list matched by reference
                    handler_by_reference = {}

                    for (event, handlers) in results:
                        for handler_controller in handlers:
                            for reference in handler_controller.handler.when.references:
                                handler_by_reference.setdefault(handler_controller, set()).add(
                                    reference
                                )

                    cache = await event_store.events_happened(list(chain.from_iterable(handler_by_reference.values())))
                    after_cache = time.perf_counter()
                    api.logger.debug(f"cache took {after_cache - before_cache} seconds")

                    for (event, handlers) in results:
                        if not handlers:
                            api.logger.debug(
                                "No handler found for events"
                            )

                        before_all_handlers = time.perf_counter()

                        futures = []

                        for handler in handlers:
                            futures.append(handler.execute(event, event_store, cache))

                        await asyncio.gather(*futures)

                        after_all_handlers = time.perf_counter()
                        api.logger.debug(
                            f"all handlers took {after_all_handlers - before_all_handlers} seconds"
                        )

                except Exception as e:
                    raise e

                finally:
                    sessions = [
                        session for session, _ in events_with_session if session
                    ]
                    if sessions:
                        before_lock = time.perf_counter()
                        for session in sessions:
                            await handler_store.unlock(session)
                        after_lock = time.perf_counter()
                        api.logger.debug(
                            f"unlock took {after_lock - before_lock} seconds"
                        )

                after_start = time.perf_counter()
                api.logger.debug(f"executor took {after_start - before_start} seconds")
                api.logger.debug("Event store unlocked")

        return executor
