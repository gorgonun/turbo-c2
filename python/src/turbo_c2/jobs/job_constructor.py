from __future__ import annotations
import asyncio
import functools
from types import SimpleNamespace
from typing import Any, Callable, Generic, Type, TypeVar

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
from turbo_c2.jobs.job_input_spec import (
    JobInputSpec,
    JobInputSpecQueuesMultipleSpec,
    JobInputSpecQueuesSingleSpec,
    JobInputSpecQueuesSpec,
)
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.queues.consumer import Consumer
from turbo_c2.globals.ebf_global import get_scheduler_globals
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition


T = TypeVar("T")
U = TypeVar("U")
P = TypeVar("P", bound=JobParameter)


class JobConstructor(Generic[T, U]):
    def __init__(
        self,
        queue: QueueReference | None = None,
        next_job: JobConstructor | None = None,
        definition: DynamicJobDefinition | None = None,
        job_instance: JobInstance | None = None,
        queues: list[QueueDefinition] | None = None,
        group_path: str = "root",
        queue_apis: dict[str, QueueApi] | None = None,
    ) -> None:
        self.__queue = queue
        self.__next_job: JobConstructor | None = next_job
        self.__definition: DynamicJobDefinition | None = definition
        self.__job_instance: JobInstance | None = job_instance
        self.__queues: list[QueueDefinition] = queues or []
        self.__group_path: str = group_path
        self.__queue_apis = queue_apis or {}

    @property
    def name(self) -> str:
        return self.__definition.name

    @property
    def definition(self) -> DynamicJobDefinition | None:
        return self.__definition

    @property
    def job_instance(self) -> JobInstance | None:
        return self.__job_instance

    @property
    def next_job(self) -> JobConstructor | None:
        return self.__next_job

    def add_job_definition(
        self,
        run_function: Callable[[T], U],
        *args,
        name: str | None = None,
        wait_time: int = 1,
        single_run: bool = False,
        tuple_result_is_single_value: bool = False,
        clients_with_context: dict[str, Any] | None = None,
        representation: NodeRepresentation | None = None,
        meta: dict[str, Any] | None = None,
        on_init: Callable[[SimpleNamespace], None] | None = None,
        iterable_chunk_size: int = 1,
        spec: JobInputSpec | None = None,
        disable_content_wrap: bool = False,
        **kwargs,
    ):
        self.__definition = DynamicJobDefinition(
            name=name or run_function.__name__,
            run_function=run_function,
            description=run_function.__doc__.strip() if run_function.__doc__ else None,
            args=args,
            wait_time=wait_time,
            single_run=single_run,
            tuple_result_is_single_value=tuple_result_is_single_value,
            clients_with_context=clients_with_context,
            kwargs=kwargs,
            spec=spec,
            meta={
                "created_by": "job_constructor",
                "representation": representation or NodeRepresentation.ACTION,
                **(meta or {}),
            },
            on_init=on_init,
            iterable_chunk_size=iterable_chunk_size,
            disable_content_wrap=disable_content_wrap,
        )

        return self

    def add_job_instance(
        self,
        input_queue_reference: list[QueueReference] | None = None,
        extra_queues_references: list[QueueReference] | None = None,
        output_queues_references: list[QueueReference] | None = None,
        replicas: int | None = None,
        replication_mode: RemoteJobReplicaMode | None = None,
        read_only: bool = True,
        instance_parameters: P | None = None,
        group_path: str | None = None,
    ):
        self.__group_path = group_path or "root"

        replication_mode = (
            replication_mode or replication_mode or RemoteJobReplicaMode.FOLLOW_QUEUE
            if extra_queues_references and input_queue_reference is None
            else RemoteJobReplicaMode.MANUAL_SETTING
        )

        self.__job_instance = JobInstance(
            job_definition=self.__definition,
            replicas=replicas if replicas is not None else 1,
            replication_mode=replication_mode,
            read_only=read_only,
            group_path=self.__group_path,
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
        )

        self.__queues = (
            [QueueDefinition(input_queue_reference)]
            if input_queue_reference
            else []
            + [QueueDefinition(queue) for queue in (extra_queues_references or [])]
            + [QueueDefinition(output) for output in (output_queues_references or [])]
        )

        return self

    def local_register(self, register: SchedulerGlobals):
        if self.__definition:
            get_scheduler_globals().add_job(
                self.__definition,
            )

        if self.__queues:
            get_scheduler_globals().add_queues(self.__queues)

        get_scheduler_globals().create_job_group(
            name=self.__group_path,
            path=self.__group_path,
            meta={"created_by": "job_constructor"},
            description="Job group created by job constructor",
        )

        if self.__job_instance:
            get_scheduler_globals().add_job_instance_to_group(
                self.__job_instance, self.__group_path
            )

        return self
    
    async def evaluate_queues(self, central_api: CentralApi):
        if self.__job_instance:
            for queue_definition in self.__queues:
                if queue_definition.name not in self.__queue_apis:
                    queue: QueueApi = await central_api.execute(
                        CreateQueueCommand(QueueDefinition(queue_definition.name), fail_if_exists=False)
                    )

                    self.__queue_apis[queue_definition.name] = queue

    async def remote_create_queues(self, central_api: CentralApi):
        await asyncio.gather(
            *[
                central_api.execute(
                    CreateQueueCommand(queue_definition)
                    for queue_definition in self.__queues
                )
            ]
        )

    async def remote_create_group(self, central_api: CentralApi):
        job_group = JobGroupWithInstances(
            name=self.__group_path,
            path=self.__group_path,
            meta={"created_by": "job_constructor"},
            description="Job group created by job constructor",
        )

        await central_api.execute(GroupCrud.create(job_group, job_group.path))

    async def remote_create_definition(self, central_api: CentralApi):
        await central_api.execute(
            JobDefinitionCrud.create(
                self.__definition,
                self.__definition.resource_id,
            )
        )

    async def remote_create_instance(self, central_api: CentralApi):
        job_instance_data = JobInstanceData(
            job_definition_id=self.__definition.resource_id,
            replicas=self.__job_instance.replicas,
            replication_mode=self.__job_instance.replication_mode,
            read_only=self.__job_instance.read_only,
            input_queue_reference=self.__job_instance.input_queue_reference,
            extra_queues_references=self.__job_instance.extra_queues_references,
            output_queues_references=self.__job_instance.output_queues_references,
            parameters=self.__job_instance.parameters,
            name=self.__job_instance.name or self.__definition.name,
            group_path=self.__group_path,
        )

        await central_api.execute(
            CreateExternalJobInstanceCommand(job_instance_data=job_instance_data)
        )

    async def remote_register(
        self,
        central_api: CentralApi,
        create_queues: bool | None = None,
        create_definition: bool | None = None,
        create_group: bool | None = None,
        create_instance: bool | None = None,
    ):

        if (create_queues is None and self.__queues) or create_queues:
            await self.remote_create_queues(central_api)

        if (create_definition is None and self.__definition) or create_definition:
            await self.remote_create_definition(central_api)

        if (create_group is None and self.__group_path) or create_group:
            await self.remote_create_group(central_api)

        if (create_instance is None and self.__job_instance) or create_instance:
            await self.remote_create_instance(central_api)

        return self

    def then(self, job_constructor: JobConstructor[T, U]) -> JobConstructor:
        self.__next_job = job_constructor
        self.__queue = QueueDefinition(
            NameUtils.get_anonymous_name(f"Queue{{Job/{self.name}}}")
        )
        get_scheduler_globals().add_queue(self.__queue)
        return job_constructor

    def collect(self) -> Consumer[U]:
        queue_definition = QueueDefinition(
            NameUtils.get_anonymous_name(f"Queue{{Job/{self.name}}}")
        )
        consumer = Consumer(
            queue_definition,
            NameUtils.get_anonymous_name(f"Consumer{{Job/{self.name}}}"),
        )
        get_scheduler_globals().add_needs_queue_evaluation(consumer)
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
                "job_definition_id": self.__definition.resource_id,
            },
        )
        return await central_api.execute(
            CreateExternalJobInstanceCommand(job_instance_data=job_instance_data)
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__definition.run_function(*args, **kwds)

    def __hash__(self) -> int:
        return hash(self.__definition)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, JobConstructor):
            return self.__definition == o.definition
        return False

    def __reduce__(self) -> str | tuple[Any, ...]:
        return (
            functools.partial(
                JobConstructor,
                queue=self.__queue,
                next_job=self.__next_job,
                definition=self.__definition,
                job_instance=self.__job_instance,
                queues=self.__queues,
                group_path=self.__group_path,
            ),
            tuple(),
        )

    @staticmethod
    def create_job_spec(
        input_queue_reference: list[QueueReference] | None = None,
        extra_queues_references: list[QueueReference] | None = None,
        output_queues_references: list[QueueReference] | None = None,
        parameters: Type[P] | None = None,
    ):
        return JobInputSpec(
            queues=JobInputSpecQueuesSpec(
                input_queue=(
                    JobInputSpecQueuesSingleSpec(None)
                    if input_queue_reference
                    else None
                ),
                extra_queues=(
                    JobInputSpecQueuesMultipleSpec(None, len(extra_queues_references))
                    if extra_queues_references
                    else None
                ),
                output_queues=(
                    JobInputSpecQueuesMultipleSpec(None, len(output_queues_references))
                    if output_queues_references
                    else None
                ),
            ),
            parameters=parameters,
        )
