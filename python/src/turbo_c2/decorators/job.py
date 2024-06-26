from types import SimpleNamespace
from typing import Any, Callable

from turbo_c2.abstractions.job_parameter import JobParameter
from turbo_c2.globals.ebf_global import get_scheduler_globals
from turbo_c2.jobs.job_definition_constructor import JobDefinitionConstructor
from turbo_c2.jobs.job_instance_constructor import JobInstanceConstructor


def job(
    *args,
    name=None,
    input_queue_reference=None,
    extra_queues_references=None,
    output_queues_references=None,
    wait_time=1,
    single_run=False,
    clients_with_context=None,
    replicas=1,
    replication_mode=None,
    group_path=None,
    representation=None,
    meta=None,
    on_init: Callable[[SimpleNamespace], None] | None = None,
    parameters: JobParameter | None = None,
    instance_parameters: JobParameter | None = None,
    iterable_chunk_size=1,
    job_instance_args: tuple | None = None,
    job_instance_kwargs: dict | None = None,
    tuple_result_is_single_value=False,
    disable_content_wrap=False,
    register=True,
    **kwargs,
) -> Callable[..., JobInstanceConstructor]:
    def wrapped(func: Callable[..., Any]) -> JobInstanceConstructor:
        job_constructor = JobDefinitionConstructor.from_data(
            func,
            *args,
            **{
                **kwargs,
                "name": name,
                "wait_time": wait_time,
                "single_run": single_run,
                "tuple_result_is_single_value": tuple_result_is_single_value,
                "clients_with_context": clients_with_context,
                "representation": representation,
                "meta": meta,
                "on_init": on_init,
                "iterable_chunk_size": iterable_chunk_size,
                "input_queue_reference": input_queue_reference,
                "extra_queues_references": extra_queues_references,
                "output_queues_references": output_queues_references,
                "parameters": parameters,
                "disable_content_wrap": disable_content_wrap,
            }
        ).set(
            *(job_instance_args or []),
            **{
                **(job_instance_kwargs or {}),
                "input_queue_reference": input_queue_reference,
                "extra_queues_references": extra_queues_references,
                "output_queues_references": output_queues_references,
                "replicas": replicas,
                "replication_mode": replication_mode,
                "group_path": group_path,
                "instance_parameters": instance_parameters,
            }
        ).evaluate_instances()

        if register:
            job_constructor.local_register(get_scheduler_globals())

        return job_constructor

    return wrapped
