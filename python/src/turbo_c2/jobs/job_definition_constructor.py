from __future__ import annotations
from dataclasses import dataclass, field, replace
import functools
from types import SimpleNamespace
from typing import Any, Callable, Generic, Type, TypeVar

from turbo_c2.abstractions.job_parameter import JobParameter
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.globals.scheduler_globals import SchedulerGlobals
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.jobs.job_input_spec import (
    JobInputSpec,
    JobInputSpecQueuesMultipleSpec,
    JobInputSpecQueuesSingleSpec,
    JobInputSpecQueuesSpec,
)
from turbo_c2.jobs.job_instance_constructor import JobInstanceConstructor
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.jobs.remote_job_replica_mode import RemoteJobReplicaMode
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition


T = TypeVar("T")
U = TypeVar("U")
P = TypeVar("P", bound=JobParameter)


@dataclass(frozen=True)
class JobDefinitionConstructor(Generic[T, U]):
    definition: DynamicJobDefinition
    next_jobs: list[JobDefinitionConstructor] = field(default_factory=list)
    previous_queue: QueueReference | None = None
    previous_jobs: list[JobDefinitionConstructor] = field(default_factory=list)
    args: list[tuple[Any]] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)

    def add_next_job(
        self, next_job: JobDefinitionConstructor
    ) -> JobDefinitionConstructor:
        return replace(self, next_jobs=self.next_jobs + [next_job])

    def add_previous_job(
        self, previous_job: JobDefinitionConstructor
    ) -> JobDefinitionConstructor:
        return replace(self, previous_jobs=self.previous_jobs + [previous_job])

    def reset_next_jobs(self) -> JobDefinitionConstructor:
        return replace(self, next_jobs=[])

    def reset_previous_jobs(self) -> JobDefinitionConstructor:
        return replace(self, previous_jobs=[])

    def set_previous_queue(
        self, previous_queue: QueueDefinition
    ) -> JobDefinitionConstructor:
        return replace(self, previous_queue=previous_queue)

    def local_register(self, register: SchedulerGlobals):
        if self.definition:
            register.add_job(
                self.definition,
            )

        return self

    async def remote_register(
        self,
        central_api: CentralApi,
    ):
        if self.definition:
            await self.remote_create_definition(central_api)

        return self

    async def remote_create_definition(self, central_api: CentralApi):
        await central_api.execute(
            JobDefinitionCrud.create(
                self.definition,
                self.definition.resource_id,
            )
        )

    def then(
        self,
        job_definition_constructor: JobDefinitionConstructor[T, U],
        *args,
        input_queue_reference: QueueReference | None = None,
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
        **kwargs,
    ) -> JobDefinitionConstructor:
        if input_queue_reference:
            previous_queue = input_queue_reference
        else:
            previous_queue = NameUtils.get_anonymous_name(
                f"queue_for_job_{self.definition.name}"
            )

        job_definition_constructor_with_params = job_definition_constructor.set(
            *args,
            input_queue_reference=previous_queue,
            extra_queues_references=extra_queues_references,
            output_queues_references=output_queues_references,
            replicas=replicas,
            replication_mode=replication_mode,
            read_only=read_only,
            instance_parameters=instance_parameters,
            group_path=group_path,
            name=name,
            num_cpus=num_cpus,
            memory=memory,
            scheduling_strategy=scheduling_strategy,
            **kwargs,
        ).add_previous_job(
            replace(
                self,
                next_jobs=[*self.next_jobs, job_definition_constructor],
                previous_queue=previous_queue,
            )
        )

        return job_definition_constructor_with_params

    def set(
        self,
        *args,
        input_queue_reference: QueueReference | None = None,
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
        **kwargs,
    ) -> JobDefinitionConstructor:
        return replace(
            self,
            args=args,
            kwargs={
                **kwargs,
                "input_queue_reference": input_queue_reference,
                "extra_queues_references": extra_queues_references,
                "output_queues_references": output_queues_references,
                "replicas": replicas,
                "replication_mode": replication_mode,
                "read_only": read_only,
                "instance_parameters": instance_parameters,
                "group_path": group_path,
                "name": name,
                "num_cpus": num_cpus,
                "memory": memory,
                "scheduling_strategy": scheduling_strategy,
            },
            previous_queue=input_queue_reference,
        )

    def evaluate_instances(
        self, output_queues_references=None
    ) -> JobInstanceConstructor:
        previous_queue = self.kwargs.pop("input_queue_reference", self.previous_queue)
        previous_instances = [
            definition.evaluate_instances(output_queues_references=[previous_queue])
            for definition in self.previous_jobs
        ]

        return JobInstanceConstructor(
            JobInstanceConstructor.create_job_instance(
                *self.args,
                definition=self.definition,
                input_queue_reference=previous_queue,
                output_queues_references=(output_queues_references or [])
                + (self.kwargs.pop("output_queues_references", None) or []),
                **self.kwargs,
            ),
            [],
            previous_instances,
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.definition.run_function(*args, **kwds)

    def __hash__(self) -> int:
        return hash(self.definition)

    def __eq__(self, o: object) -> bool:
        return self.definition == getattr(o, "definition")

    def __reduce__(self) -> str | tuple[Any, ...]:
        return (
            functools.partial(
                JobDefinitionConstructor,
                definition=self.definition,
                next_jobs=self.next_jobs,
                previous_jobs=self.previous_jobs,
            ),
            tuple(),
        )

    @classmethod
    def create_job_definition(
        cls,
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
        return DynamicJobDefinition(
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

    @classmethod
    def from_data(
        cls,
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
        input_queue_reference: list[QueueReference] | None = None,
        extra_queues_references: list[QueueReference] | None = None,
        output_queues_references: list[QueueReference] | None = None,
        parameters: Type[P] | None = None,
        **kwargs,
    ):
        spec = spec or cls.create_job_spec(
            input_queue_reference=input_queue_reference,
            extra_queues_references=extra_queues_references,
            output_queues_references=output_queues_references,
            parameters=parameters,
        )

        return cls(
            cls.create_job_definition(
                run_function=run_function,
                *args,
                name=name,
                wait_time=wait_time,
                single_run=single_run,
                tuple_result_is_single_value=tuple_result_is_single_value,
                clients_with_context=clients_with_context,
                representation=representation,
                meta=meta,
                on_init=on_init,
                iterable_chunk_size=iterable_chunk_size,
                spec=spec,
                **kwargs,
            )
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
