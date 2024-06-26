from asyncio import as_completed
import asyncio
import contextlib

from prometheus_client import Summary
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.domain.job.new_job_created import NewJobCreated
from turbo_c2.domain.scheduler.waitable_item import WaitableItem
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import PrometheusMetricsApi
from turbo_c2.interfaces.job_api import JobApi

from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.scheduler.scheduler import Scheduler


class RemoteScheduler(Scheduler):

    def __init__(self, jobs: list[JobApi], queue: QueueApi[NewJobCreated], waitable_queue: QueueApi[WaitableItem], central_api: DefaultCentralApi, metrics_client: PrometheusMetricsApi) -> None:
        super().__init__(jobs, queue)
        self.__metrics_client = metrics_client
        self.__jobs_to_monitor = {}
        self.__waitables_to_monitor = {}
        self.__waitable_queue = waitable_queue

    async def start(self):
        async def wait_job_and_return(job):
            await job.wait_finished()
            return job, "job"
        
        async def wait_waitable_and_return(waitable, name):
            await waitable
            return name, "waitable"

        for job in self.jobs:
            name = await job.get_name()
            self.__jobs_to_monitor[name] = wait_job_and_return(job)

        await asyncio.gather(*[job.start() for job in self.jobs])

        jobs_size = len(self.jobs)
        shutdown = False
        e = None
        exceptions = []
        failed_job_names = []

        while not shutdown and jobs_size > 0:
            futures = [*list(self.__jobs_to_monitor.values()), *list(self.__waitables_to_monitor.values())]
            with contextlib.suppress(asyncio.TimeoutError):
                for completed_future in as_completed(futures, timeout=1):
                    future_result, future_type = await completed_future

                    if future_type == "job":
                        job_name = await future_result.get_name()
                        del self.__jobs_to_monitor[job_name]
                        jobs_size = len(self.__jobs_to_monitor)

                        print(f"Finished job {job_name} ({jobs_size} jobs running)")

                        if await future_result.failed():
                            failed_job_names.append(job_name)
                            exceptions = await future_result.exceptions()

                            print(f"Failed job detected -> {job_name}.", exceptions)

                            shutdown = True
                            break

                        if jobs_size == 0:
                            shutdown = True
                            break

                    elif future_type == "waitable":
                        name, _ = future_result
                        del self.__waitables_to_monitor[name]
                        print(f"Finished waitable {name}")

            if await self.queue.qsize() > 0:
                async for new_job in self.queue:
                    new_job_name = await new_job.job_api.get_name()
                    print("New job detected", new_job_name)
                    jobs_size += 1
                    await new_job.job_api.start()
                    self.__jobs_to_monitor[new_job_name] = wait_job_and_return(new_job.job_api)

            if await self.__waitable_queue.qsize() > 0:
                async for waitable in self.__waitable_queue:
                    name = waitable.name
                    print("New waitable detected", name)
                    self.__waitables_to_monitor[name] = wait_waitable_and_return(waitable.wait_function(), name)

        if jobs_size > 0:
            print("Failure detected. It will be propagated to all jobs.")
            for job in self.__jobs_to_monitor.values():
                try:
                    await asyncio.wait_for(job.graceful_shutdown(), 1)

                except asyncio.TimeoutError as e:
                    print("Timeout error on job", job.get_name())

            for awaitable in self.__waitables_to_monitor.values():
                try:
                    await asyncio.wait_for(awaitable.graceful_shutdown_function(), 1)

                except asyncio.TimeoutError as e:
                    print("Timeout error on waitable", awaitable.name)

            if len(exceptions) == 1:
                raise exceptions[0]
            raise RuntimeError(exceptions)

        print("All jobs finished successfully.")
