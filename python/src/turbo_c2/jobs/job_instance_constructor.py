from __future__ import annotations
import asyncio
import functools
from typing import Any, Generic, TypeVar

from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.abstractions.job_parameter import JobParameter
from turbo_c2.extra_api.command.group.group_crud import GroupCrud
from turbo_c2.extra_api.command.job.create_external_job_instance_command import (
    CreateExternalJobInstanceCommand,
)
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.extra_api.command.queue.create_queue_command import CreateQueueCommand
from turbo_c2.globals.scheduler_globals import SchedulerGlobals
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.queues.consumer import Consumer
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition


T = TypeVar("T")
U = TypeVar("U")
P = TypeVar("P", bound=JobParameter)


class JobInstanceConstructor(Generic[T, U]):
    def __init__(
        self,
        job_instance: JobInstance,
        next_jobs: list[JobInstanceConstructor] | None = None,
        previous_jobs: list[JobInstanceConstructor] | None = None,
        queue_apis: dict[str, QueueApi] | None = None,
        definition_registered: bool = False,
        queues_created: bool = False,
        group_created: bool = False,
        instances_api: dict[str, JobApi] | None = None,
    ) -> None:
        self.__next_jobs: list[JobInstanceConstructor] = next_jobs or []
        self.__previous_jobs: list[JobInstanceConstructor] = previous_jobs or []
        self.__job_instance: JobInstance = job_instance
        self.__queue_apis = queue_apis or {}
        self.__definition_registered = definition_registered
        self.__queues_created = queues_created
        self.__group_created = group_created
        self.__instances_api = instances_api or {}

    @property
    def name(self) -> str:
        return self.job_instance.job_definition.name

    @property
    def definition(self) -> DynamicJobDefinition | None:
        return self.job_instance.job_definition

    @property
    def job_instance(self) -> JobInstance:
        return self.__job_instance

    @property
    def next_job(self) -> JobInstanceConstructor | None:
        return self.__next_jobs

    @property
    def previous_jobs(self) -> list[JobInstanceConstructor]:
        return self.__previous_jobs

    @property
    def instances_api(self) -> dict[str, dict[str, JobApi]]:
        return self.__instances_api

    def local_register(
        self,
        register: SchedulerGlobals,
        register_definition: bool = True,
        create_queues: bool = True,
        create_group: bool = True,
        register_instance: bool = True,
    ):
        if register_definition and not self.__definition_registered:
            register.add_job(
                self.__job_instance.job_definition,
            )

        queues = self.get_queues_from_instance(self.__job_instance)

        if queues and create_queues and not self.__queues_created:
            register.add_queues(queues)

        if create_group and not self.__group_created:
            register.create_job_group(
                name=self.job_instance.group_path,
                path=self.job_instance.group_path,
                meta={"created_by": "job_constructor"},
                description="Job group created by job constructor",
            )

        if register_instance:
            register.add_job_instance_to_group(
                self.__job_instance, self.job_instance.group_path
            )

        return self

    async def evaluate_queues(self, central_api: CentralApi):
        if self.__job_instance:
            for queue_definition in self.get_queues_from_instance(self.__job_instance):
                if queue_definition.name not in self.__queue_apis:
                    queue: QueueApi = await central_api.execute(
                        CreateQueueCommand(
                            QueueDefinition(queue_definition.name), fail_if_exists=False
                        )
                    )

                    self.__queue_apis[queue_definition.name] = queue

    async def remote_create_queues(self, central_api: CentralApi):
        await asyncio.gather(
            *[
                central_api.execute(
                    CreateQueueCommand(queue_definition, fail_if_exists=False)
                )
                for queue_definition in self.get_queues_from_instance(
                    self.__job_instance
                )
            ]
        )

    async def remote_create_group(self, central_api: CentralApi):
        job_group = JobGroupWithInstances(
            name=self.job_instance.group_path,
            path=self.job_instance.group_path,
            meta={"created_by": "job_constructor"},
            description="Job group created by job constructor",
        )

        await central_api.execute(
            GroupCrud.create(job_group, job_group.path, fail_if_exists=False)
        )

    async def remote_create_definition(self, central_api: CentralApi):
        await central_api.execute(
            JobDefinitionCrud.create(
                self.job_instance.job_definition,
                self.job_instance.job_definition.resource_id,
                fail_if_exists=False,
            )
        )

    async def remote_create_instance(self, central_api: CentralApi) -> list[JobApi]:
        job_instance_data = JobInstanceData(
            job_definition_id=self.__job_instance.job_definition.resource_id,
            replicas=self.__job_instance.replicas,
            replication_mode=self.__job_instance.replication_mode,
            read_only=self.__job_instance.read_only,
            input_queue_reference=self.__job_instance.input_queue_reference,
            extra_queues_references=self.__job_instance.extra_queues_references,
            output_queues_references=self.__job_instance.output_queues_references,
            parameters=self.__job_instance.parameters,
            name=self.__job_instance.name or self.__job_instance.job_definition.name,
            group_path=self.__job_instance.group_path,
            num_cpus=self.__job_instance.num_cpus,
            memory=self.__job_instance.memory,
            scheduling_strategy=self.__job_instance.scheduling_strategy,
        )

        return await central_api.execute(
            CreateExternalJobInstanceCommand(job_instance_data=job_instance_data)
        )

    async def remote_register(
        self,
        central_api: CentralApi,
        create_queues: bool = True,
        create_definition: bool = True,
        create_group: bool = True,
        create_instance: bool = True,
    ):
        updated_instances = await asyncio.gather(
            *[
                job.remote_register(
                    central_api,
                    create_queues=create_queues,
                    create_definition=create_definition,
                    create_group=create_group,
                    create_instance=create_instance,
                )
                for job in [*self.__previous_jobs, *self.__next_jobs]
            ]
        )

        new_instances = {
            "instance": {},
            "definition": {},
        }

        for instance_dict in [
            updated_instance.instances_api for updated_instance in updated_instances
        ]:
            for key, value in instance_dict.items():
                new_instances.setdefault(key, value).update(value)

        if create_queues and not self.__queues_created:
            await self.remote_create_queues(central_api)

        if create_definition and not self.__definition_registered:
            await self.remote_create_definition(central_api)

        if create_group and not self.__group_created:
            await self.remote_create_group(central_api)

        if create_instance:
            new_instance_result = await self.remote_create_instance(central_api)
            for new_instance in new_instance_result:
                instance_id = (await new_instance.get_job_instance()).resource_id
                new_instances["instance"][instance_id] = new_instance
                new_instances["definition"][
                    self.job_instance.job_definition.name
                ] = new_instance

        self.__instances_api = new_instances
        return self

    def local_collect(self, register: SchedulerGlobals) -> Consumer[U]:
        queue_definition = QueueDefinition(
            NameUtils.get_anonymous_name(f"Queue{{Job/{self.name}}}")
        )
        consumer = Consumer(
            queue_definition,
            NameUtils.get_anonymous_name(f"Consumer{{Job/{self.name}}}"),
        )
        register.add_queues([queue_definition])
        register.add_needs_queue_evaluation(consumer)
        self.job_instance.output_queues_references.append(
            QueueReference(queue_definition)
        )

        return consumer

    async def remote_collect(self, central_api: CentralApi) -> Consumer[U]:
        queue_definition = QueueDefinition(
            NameUtils.get_anonymous_name(f"Queue{{Job/{self.name}}}")
        )

        consumer = Consumer(
            queue_definition,
            NameUtils.get_anonymous_name(f"Consumer{{Job/{self.name}}}"),
        )

        self.job_instance.output_queues_references.append(
            QueueReference(queue_definition)
        )

        await central_api.execute(CreateQueueCommand(queue_definition))

        await self.evaluate_queues(central_api)

        await consumer.evaluate_queues(self.__queue_apis)

        return consumer

    async def create_new_instance(
        self,
        central_api: CentralApi,
        replicas: int,
        replication_mode: RemoteJobReplicaMode,
        read_only: bool,
        group_path: str,
        *args,
        input_queue_reference: QueueReference | None = None,
        extra_queues_references: list[QueueReference] | None = None,
        output_queues_references: list[QueueReference] | None = None,
        parameters: P | None = None,
        name: str | None = None,
        num_cpus: float | None = None,
        memory: int | None = None,
        scheduling_strategy: str = "SPREAD",
        **kwargs,
    ) -> JobApi:
        job_instance_data = JobInstanceData[P](
            *args,
            **{
                **kwargs,
                "replicas": replicas,
                "replication_mode": replication_mode,
                "read_only": read_only,
                "group_path": group_path,
                "input_queue_reference": input_queue_reference,
                "extra_queues_references": extra_queues_references,
                "output_queues_references": output_queues_references,
                "parameters": parameters,
                "name": name,
                "job_definition_id": self.definition.resource_id,
                "num_cpus": num_cpus,
                "memory": memory,
                "scheduling_strategy": scheduling_strategy,
            },
        )
        return await central_api.execute(
            CreateExternalJobInstanceCommand(job_instance_data=job_instance_data)
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__job_instance.job_definition.run_function(*args, **kwds)

    def __hash__(self) -> int:
        return hash(self.__job_instance)

    def __eq__(self, o: object) -> bool:
        return self.job_instance == getattr(o, "job_instance")

    def __reduce__(self) -> str | tuple[Any, ...]:
        return (
            functools.partial(
                JobInstanceConstructor,
                job_instance=self.job_instance,
                next_job=self.next_job,
                previous_jobs=self.previous_jobs,
                queue_apis=self.__queue_apis,
                definition_registered=self.__definition_registered,
                queues_created=self.__queues_created,
                group_created=self.__group_created,
                instances_api=self.__instances_api,
            ),
            tuple(),
        )

    @classmethod
    def create_job_instance(
        cls,
        definition: DynamicJobDefinition,
        input_queue_reference: list[QueueReference] | None = None,
        extra_queues_references: list[QueueReference] | None = None,
        output_queues_references: list[QueueReference] | None = None,
        replicas: int | None = None,
        replication_mode: RemoteJobReplicaMode | None = None,
        read_only: bool = True,
        instance_parameters: P | None = None,
        group_path: str | None = None,
        name: str | None = None,
        num_cpus: float | None = None,
        memory: int | None = None,
        scheduling_strategy: str = "SPREAD",
    ):
        replication_mode = (
            replication_mode or replication_mode or RemoteJobReplicaMode.FOLLOW_QUEUE
            if extra_queues_references and input_queue_reference is None
            else RemoteJobReplicaMode.MANUAL_SETTING
        )

        job_instance = JobInstance(
            job_definition=definition,
            replicas=replicas if replicas is not None else 1,
            replication_mode=replication_mode,
            read_only=read_only,
            group_path=group_path or "root",
            input_queue_reference=(
                input_queue_reference if input_queue_reference else None
            ),
            extra_queues_references=[
                queue for queue in (extra_queues_references or [])
            ],
            output_queues_references=[
                queue for queue in (output_queues_references or [])
            ],
            parameters=instance_parameters,
            name=name or definition.name,
            num_cpus=num_cpus,
            memory=memory,
            scheduling_strategy=scheduling_strategy,
        )

        return job_instance

    @staticmethod
    def get_queues_from_instance(job_instance: JobInstance) -> list[QueueDefinition]:
        return (
            [QueueDefinition(job_instance.input_queue_reference)]
            if job_instance.input_queue_reference
            else []
            + [
                QueueDefinition(queue)
                for queue in (job_instance.extra_queues_references or [])
            ]
            + [
                QueueDefinition(output)
                for output in (job_instance.output_queues_references or [])
            ]
        )
