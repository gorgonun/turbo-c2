import asyncio
import contextlib
from typing import Any, Coroutine
import ray
from turbo_c2.clients.prometheus.remote_prometheus_metrics_api import Gauge
from turbo_c2.extra_api.command.job.job_type_definition import JobTypeDefinition
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import PrometheusMetricsApi
from turbo_c2.jobs import job_instance
from turbo_c2.jobs.dynamic_job.dynamic_job import DynamicJob
from turbo_c2.jobs.default_job_controller import DefaultJobController
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition
from turbo_c2.interfaces.queue_api import QueueApi
from ray.exceptions import RayActorError


# TODO: Async with wait function
class RemoteJobController(DefaultJobController[JobInstance]):
    def __init__(
        self,
        job_instance: JobInstance,
        metrics_client: PrometheusMetricsApi,
        start_number_of_replicas: int | None = None,
    ) -> None:
        super().__init__(job_instance, start_number_of_replicas or job_instance.replicas)
        self.__actors: list[DynamicJob] = []
        self.__runs: dict[str, DynamicJob] = {}
        self.__ready_refs: list[Any] = []
        self.__finished = False
        self.__successful = False
        self.__exceptions = []
        self.__replication_mode = job_instance.replication_mode
        self.__evaluated_queues = {}
        self.__logger = TurboLogger("RemoteJobController")
        self.__metrics_client = metrics_client
        self.__has_started = None
        self.metrics_created = False
        self.__metrics = {}
        self.__state = "started"

    @property
    def tc2_job_replicas_counter(self) -> Gauge:
        metric = self.__metrics.get("tc2_job_replicas_counter")

        if not metric:
            raise ValueError("Metric not found")
        
        return metric

    async def create_metrics(self):
        if not self.metrics_created:
            self.__metrics["tc2_job_replicas_counter"] = await self.__metrics_client.gauge(
                "tc2_job_replicas_counter",
                "Job replicas",
                labels={"job_name": self.job_instance.name, "job_id": self.job_instance.resource_id}
            )

            self.metrics_created = True

    def get_target_replicas(self):
        if self.__replication_mode == RemoteJobReplicaMode.MANUAL_SETTING:
            return self.start_number_of_replicas
        if self.__replication_mode == RemoteJobReplicaMode.FOLLOW_QUEUE:
            if isinstance(self.job_instance.job_definition, DynamicJobDefinition):
                return len(self.job_instance.extra_queues_references)
            raise RuntimeError(f"Job {self.job_instance.name} is not a DynamicJob")
        raise RuntimeError(f"Unknown replication mode {self.__replication_mode}")

    async def start(self, replicas: int | None = None):
        await self.create_metrics()

        if not self.__has_started:
            self.__has_started = asyncio.Lock()

        if not self.__has_started.locked():
            await self.__has_started.acquire()

        fixed_replicas = replicas or self.get_target_replicas()

        self.__logger.info(
            f"Starting remote controller for {self.job_instance.name} with {fixed_replicas} replicas"
        )

        await self.scale(fixed_replicas)

        await super().start(fixed_replicas)

    async def scale(self, replicas: int):
        await self.create_metrics()
        self.__logger.info(f"Scaling job {self.job_instance.name} with {replicas} replicas")
        job_type = await self.__central_api.execute(JobTypeDefinition.get(type(self.job_instance.job_definition)))

        if replicas - self.replicas == 0:
            self.__logger.info(f"Replicas are the same for {self.job_instance.name}")
            return
        
        if replicas < self.replicas:
            self.__logger.info(f"Scaling down {self.job_instance.name}")
            await self.graceful_shutdown(self.replicas - replicas)
            self.replicas = replicas
            return

        for i in range(replicas - self.replicas):
            self.__logger.info(f"Scaling up {self.job_instance.name}")
            await self.tc2_job_replicas_counter.inc()

            self.__logger.debug(
                f"Scaling job {self.job_instance.name} to {i + 1} from {self.replicas}"
            )

            job_name = f"{self.job_instance.name}{i + 1}"
            # FIXME: This should be generic
            actor: DynamicJob = ray.remote(job_type).options(num_cpus=self.job_instance.num_cpus or 0.1, memory=self.job_instance.memory or 150 * 1024 * 1024, name=job_name, scheduling_strategy=self.job_instance.scheduling_strategy or "SPREAD").remote(self.job_instance, self.__metrics_client)
            self.__actors.append(actor)

            await actor.add_central_api.remote(self.__central_api)

            if self.__evaluated_queues:
                if not await actor.is_evaluated.remote():
                    await actor.evaluate_queues.remote(self.__evaluated_queues)

            self.__runs[job_name] = actor.run.remote()
            self.__logger.info(f"Started job {job_name} for {self.job_instance.name} with single_run = {self.job_instance.job_definition.single_run}")

            if self.job_instance.job_definition.single_run:
                if self.__has_started and self.__has_started.locked():
                    self.__has_started.release()

        await super().scale(replicas)

    async def run_return_ref_when_completed(self, ref: Any):
        try:
            await ref
        except Exception as e:  # pylint: disable=broad-except
            self.__exceptions.append(e)
        return ref

    async def wait_finished(self):
        await self.finished(None)

    async def finished(self, timeout: int | None = 0.0001):
        async def wait_return(key: str, value: Coroutine[Any, Any, Any]):
            # FIXME: Avoid kill job, let it finish
            with contextlib.suppress(RayActorError):
                await value
            return key

        if not self.__finished:

            while True:
                await asyncio.wait_for(self.__has_started.acquire(), timeout=timeout)

                self.__logger.info(f"Waiting for {self.job_instance.name} to finish")
                if len(self.__actors) == 0 and self.job_instance.job_definition.single_run:
                    self.__finished = True
                    break

                ready_refs, result_refs = await asyncio.wait(
                    list(wait_return(key, value) for key, value in self.__runs.items()), timeout=timeout
                )
                self.__finished = len(result_refs) == 0

                for ready_ref in ready_refs:
                    self.__runs.pop(ready_ref.result())
                    self.replicas -= 1
                    await self.tc2_job_replicas_counter.set(value=self.replicas)

                self.__ready_refs = ready_refs
                self.__logger.info(
                    f"Finished waiting for {self.job_instance.name} to finish",
                    ready_refs,
                    result_refs,
                )

                if self.__finished:
                    self.__has_started.release()

                if self.job_instance.job_definition.single_run:
                    break

        return self.__finished

    async def successful(self):
        if not await self.finished():
            return False

        for ready_ref in self.__ready_refs:
            try:
                await ready_ref
            except Exception as e:  # pylint: disable=broad-except
                self.__exceptions.append(e)

        self.__successful = len(self.__exceptions) == 0
        return self.__successful

    async def failed(self):
        return not await self.successful()

    async def exceptions(self):
        if not await self.finished():
            return None

        if self.__exceptions:
            return self.__exceptions

        for ready_ref in self.__ready_refs:
            try:
                await ready_ref
            except Exception as e:  # pylint: disable=broad-except
                self.__exceptions.append(e)

        return self.__exceptions

    async def evaluate_queues(self, queues: dict[QueueReference, QueueApi]):
        self.__evaluated_queues = queues
        for actor in self.__actors:
            await actor.evaluate_queues.remote(queues)

    async def pause(self):
        await asyncio.gather(*[actor.pause.remote() for actor in self.__actors])
        self.__state = "paused"

    async def resume(self):
        await asyncio.gather(*[actor.resume.remote() for actor in self.__actors])
        self.__state = "started"

    async def get_state(self):
        return self.__state

    def get_name(self):
        return self.job_instance.name

    def get_definition(self):
        return self.job_instance

    async def graceful_shutdown(self, replicas: int | None = None):
        self.__logger.info(f"Graceful shutdown for {self.job_instance.name} for replicas", replicas)
        fixed_replicas = replicas or self.replicas
        current_actors = list(self.__actors)

        for i in range(fixed_replicas):
            actor = self.__actors[i]
            await actor.graceful_shutdown.remote()

            with contextlib.suppress(RayActorError):
                ray.kill(actor)
        
        self.__actors = current_actors[fixed_replicas:]

    async def add_central_api(self, central_api: DefaultCentralApi):
        self.__logger.info(f"Adding central api to {self.job_instance.name}")
        self.__central_api = central_api

        for actor in self.__actors:
            self.__logger.info(f"Adding central api to {self.job_instance.name}")
            await actor.add_central_api.remote(central_api)
            self.__logger.info(f"Central api added to {self.job_instance.name}")
