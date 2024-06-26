from typing import Any, Callable, TypeVar
import uuid
from turbo_c2.abstractions.job_parameter import JobParameter
from turbo_c2.interfaces.dynamic_job_definition import JobDefinition
from turbo_c2.jobs.queue_configuration import QueueConfiguration


T = TypeVar("T")


class DefaultJobDefinition(JobDefinition[T]):
    def __init__(
        self,
        run_function: Callable[..., T],
        args: list[Any] | None = None,
        wait_time=1,
        single_run=False,
        clients_with_context: dict[str, Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        definition=uuid.uuid4().hex,
        input_queue: QueueConfiguration | None = None,
        output_queues: list[QueueConfiguration] | None = None,
        extra_queues: list[QueueConfiguration] | None = None,
        parameters: JobParameter | None = None,
        name: str | None = None,
        description: str | None = None,
        disable_content_wrap: bool = False,
    ):
        super().__init__(
            run_function=run_function,
            args=args or [],
            wait_time=wait_time,
            single_run=single_run,
            clients_with_context=clients_with_context or [],
            kwargs=kwargs or {},
            definition=definition,
            input_queue=input_queue,
            output_queues=output_queues or [],
            extra_queues=extra_queues or [],
            parameters=parameters,
            name=name or self.run_function.__code__.co_name,
            description=description or self.run_function.__doc__,
            disable_content_wrap=disable_content_wrap,
        )
