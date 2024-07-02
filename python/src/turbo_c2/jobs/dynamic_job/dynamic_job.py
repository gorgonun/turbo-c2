import asyncio
from collections import deque
from contextlib import ExitStack
from dataclasses import replace
import functools
import threading
import time
import traceback
from typing import Any, Callable, Coroutine, TypeVar, cast
import inspect

from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.extra_api.command.queue.get_queues_by_type_command import (
    GetQueuesByTypeCommand,
)
from turbo_c2.helpers.async_utils import async_lambda
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import (
    Counter,
    Histogram,
    PrometheusMetricsApi,
)
from turbo_c2.jobs import job_output
from turbo_c2.jobs.job_content_parameter import JobContentParameter
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_output import JobOutput
from turbo_c2.helpers.iterable_helpers import is_async_iterable, is_iterable
from turbo_c2.jobs.dynamic_job.dynamic_job_helper_api import DynamicJobHelperApi
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.jobs.remote_job import RemoteJob
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


JOB_INPUT = TypeVar("JOB_INPUT")
JOB_RESULT = TypeVar("JOB_RESULT")
JOB_PARAMETERS = TypeVar("JOB_PARAMETERS")


class DynamicJob(RemoteJob, NeedsCentralApi):
    def __init__(
        self,
        job_instance: JobInstance[JOB_RESULT, JOB_PARAMETERS],
        metrics_client: PrometheusMetricsApi,
        original_parameters: set[str] | None = None,
        handle_queue: bool | None = None,
        dynamic_job_helper_api: DynamicJobHelperApi | None = None,
        clients_created: bool | None = None,
        contexts: dict[str, Any] | None = None,
        async_run: bool | None = None,
        clients_with_context: dict[str, Any] | None = None,
        central_api: DefaultCentralApi | None = None,
        finished_event: asyncio.Event | None = None,
        evaluated_queues: dict[QueueReference, QueueApi] | None = None,
        on_init: Callable[[dict[str, Any]], None] | None = None,
        init: bool = False,
        had_first_run: bool = False,
        metrics_created: bool = False,
        metrics=None,
        pause_event: asyncio.Event | None = None,
        accumulated_write_items: list[tuple[JOB_RESULT, JOB_RESULT]] | None = None,
    ) -> None:
        """
        tuple_result_is_single_value: if true, when a job returns a tuple it will be send to queue as one single value, instead of sending each value to a different queue
        clients_with_context: clients that will be used as context managers. The context will be passed as a parameter to the job function. WARNING: all replicas share the same object. If you need to have different objects for each replica, you need to set the value as a function that returns the object.
        """
        self.__job_instance = job_instance
        self.__metrics_client = metrics_client
        self.__original_parameters = original_parameters or set(
            inspect.signature(
                self.__job_instance.job_definition.run_function
            ).parameters
        )
        self.__handle_queue = (
            handle_queue
            or "content" in self.original_parameters
            or "job_output" in self.original_parameters
            or "output" in self.original_parameters
        )
        self.__dynamic_job_helper_api: DynamicJobHelperApi | None = (
            dynamic_job_helper_api
        )
        self.__clients_created = clients_created or False
        self.__contexts: dict[str, Any] = contexts or {}
        self.__async_run = (
            async_run
            if async_run is not None
            else inspect.iscoroutinefunction(
                self.__job_instance.job_definition.run_function
            )
        )
        self.__clients_with_context = (
            clients_with_context
            or self.__job_instance.job_definition.clients_with_context
            or {}
        )

        fixed_wait_time = (
            self.__job_instance.job_definition.wait_time
            if not self.__handle_queue
            else 0
        )
        self.__fself = {}
        self.__on_init = on_init or job_instance.job_definition.on_init
        self.__init = init

        if not self.__init and self.__on_init:
            self.__on_init(self.__fself)

        self.__had_first_run = had_first_run
        self.metrics_created = metrics_created

        ## TODO: implement
        self.__checkpoint_id = None
        self.__metrics = metrics or {}
        self.__queue_by_type_cache = {}
        self.__after_send_to_output: list[
            Callable[
                [JOB_INPUT, JOB_RESULT, DynamicJobHelperApi], Coroutine[Any, Any, None]
            ]
        ] = []
        self.__content_job_output_cache: JobOutput | None = None
        self.__buffer = deque(maxlen=job_instance.buffer_size or 1)
        self.__consumed_buffer = deque(maxlen=job_instance.buffer_size or 1)
        self.__accumulated_write_items: list[tuple[JOB_INPUT, JOB_RESULT, bool]] = accumulated_write_items or []
        self.__accumulated_write_items_lock = threading.Lock()

        super().__init__(
            name=self.__job_instance.name
            or self.__job_instance.job_definition.run_function.__code__.co_name,
            wait_time=fixed_wait_time,
            single_run=self.__job_instance.job_definition.single_run,
            queues_reference=(self.__job_instance.extra_queues_references or [])
            + (
                [self.__job_instance.input_queue_reference]
                if self.__job_instance.input_queue_reference
                else []
            )
            + (self.__job_instance.output_queues_references or []),
            queues_reference_mapping=evaluated_queues,
            finished_event=finished_event,
            pause_event=pause_event,
        )
        NeedsCentralApi.__init__(self, central_api)

    @property
    def original_parameters(self):
        return self.__original_parameters

    @property
    def input_queue(self):
        return self.get_input_queue()

    @property
    def dynamic_job_helper_api(self):
        if not self.__dynamic_job_helper_api:
            self.__dynamic_job_helper_api = DynamicJobHelperApi(
                (self.get_input_reference(), self.get_input_queue()),
                self.get_queues_mapping(),
                self.get_outputs_mapping(),
                self.central_api,
                self.logger,
                self.__metrics_client,
                self.__job_instance,
                self.send_to_self,
                self.__buffer,
                self.after_consume_buffer,
            )
        return self.__dynamic_job_helper_api

    @property
    def clients_with_context(self):
        if not self.__clients_created:
            self.__clients_with_context = {
                name: client() if callable(client) else client
                for name, client in (self.__clients_with_context or {}).items()
            }
        return self.__clients_with_context

    @property
    def queues(self):
        return self.get_extra_queues()

    @property
    def outputs(self):
        return self.get_outputs()

    @property
    def tc2_input_counter(self) -> Counter:
        return self.get_metric("tc2_input_counter")

    @property
    def tc2_output_counter(self) -> Counter:
        return self.get_metric("tc2_output_counter")

    @property
    def tc2_time_between_get_content(self) -> Histogram:
        return self.get_metric("tc2_time_between_get_content")

    @property
    def tc2_time_between_function_execution(self) -> Histogram:
        return self.get_metric("tc2_time_between_function_execution")
    
    def after_consume_buffer(self, buffer_content: deque[JOB_RESULT]):
        self.__consumed_buffer.extend(buffer_content)

    async def send_accumulated_data_to_queue(self):
        if not self.__job_instance.accumulate_write_seconds:
            return

        while True:
            await asyncio.sleep(self.__job_instance.accumulate_write_seconds)
            if self.__accumulated_write_items:

                with self.__accumulated_write_items_lock:
                    targets = list(self.__accumulated_write_items)
                    self.__accumulated_write_items = []

                results_to_output = []
                results_to_self = []

                for content, result, is_self_target in targets:
                    if is_self_target:
                        results_to_self.append(result)
                    else:
                        results_to_output.append(result)

                if results_to_output:
                    await self.handle_output(
                        results_to_output, self.get_outputs()
                    )

                if results_to_self:
                    if not self.input_queue:
                        raise RuntimeError("Input queue not defined")

                    await self.handle_output(
                        results_to_self, [self.input_queue]
                    )

                for content, result, _ in targets:
                    await self.handle_after_send_to_output(content, result)

    def get_metric(self, name: str):
        metric = self.__metrics.get(name)

        if not metric:
            raise ValueError("Metric not found")

        return metric

    async def send_to_self(self, data: JOB_RESULT):
        if not self.__job_instance.accumulate_write_seconds:
            outputs = [self.input_queue]
            await self.handle_output(data, outputs)
            await self.handle_after_send_to_output(self.__content_job_output_cache, data)
            return
        
        with self.__accumulated_write_items_lock:
            self.__accumulated_write_items.append((self.__content_job_output_cache, data, True))

    async def create_metrics(self):
        self.__metrics["tc2_input_counter"] = await self.__metrics_client.counter(
            "tc2_input_counter",
            "Content received by job",
            labels={
                "job_name": self.name,
                "job_id": self.__job_instance.resource_id,
                "group_path": self.__job_instance.group_path,
            },
        )

        self.__metrics["tc2_output_counter"] = await self.__metrics_client.counter(
            "tc2_output_counter",
            "Content sent by job",
            labels={
                "job_name": self.name,
                "job_id": self.__job_instance.resource_id,
                "group_path": self.__job_instance.group_path,
            },
        )

        self.__metrics["tc2_time_between_get_content"] = (
            await self.__metrics_client.histogram(
                "tc2_time_between_get_content",
                "Time between get content from queue",
                labels={
                    "job_name": self.name,
                    "job_id": self.__job_instance.resource_id,
                    "group_path": self.__job_instance.group_path,
                },
            )
        )

        self.__metrics["tc2_time_between_function_execution"] = (
            await self.__metrics_client.histogram(
                "tc2_time_between_function_execution",
                "Time to function execution",
                labels={
                    "job_name": self.name,
                    "job_id": self.__job_instance.resource_id,
                    "group_path": self.__job_instance.group_path,
                },
            )
        )

    def if_checkpoint(self, checkpoint_id):
        return not self.__checkpoint_id or self.__checkpoint_id == checkpoint_id

    async def can_run(self):
        return True

    def get_input_queue(self):
        if self.__job_instance.input_queue_reference:
            if self.is_evaluated():
                return self.evaluated_queue_mapping[
                    self.__job_instance.input_queue_reference
                ]
        return None

    def get_input_reference(self):
        return self.__job_instance.input_queue_reference

    def get_extra_queues(self) -> list[QueueApi]:
        return list(self.get_queues_mapping().values())

    def get_queues_mapping(self):
        if self.__job_instance.extra_queues_references:
            if self.is_evaluated():
                return {
                    queue: self.evaluated_queue_mapping[queue]
                    for queue in self.__job_instance.extra_queues_references
                }

        return cast(dict[QueueReference, QueueApi], {})

    def get_extra_queues_references(self):
        return self.__job_instance.extra_queues_references

    def get_outputs(self) -> list[QueueApi]:
        return list(self.get_outputs_mapping().values())

    def get_outputs_mapping(self):
        if self.__job_instance.output_queues_references:
            if self.is_evaluated():
                return {
                    queue: self.evaluated_queue_mapping[queue]
                    for queue in self.__job_instance.output_queues_references
                }
        return cast(dict[QueueReference, QueueApi], {})

    def get_output_references(self):
        return self.__job_instance.output_queues_references

    def is_evaluated(self):
        return self.evaluated

    def get_name(self):
        return self.name

    def set_outputs(self, outputs: dict[QueueReference, Any]):
        for reference in self.__job_instance.output_queues_references:
            self.remove_queue(reference)

        self.__job_instance = replace(
            self.__job_instance, output_queues_references=list(outputs.keys())
        )
        for reference, queue in outputs.items():
            if isinstance(queue, QueueApi):
                self.add_queue(reference, queue)
            else:
                self.add_queue(reference, None)

    def set_extra_queues(self, extra_queues: dict[QueueReference, Any]):
        for reference in self.__job_instance.extra_queues_references:
            self.remove_queue(reference)

        self.__job_instance = replace(
            self.__job_instance,
            extra_queues_references=list(extra_queues.keys()),
        )

        for reference, queue in extra_queues.items():
            if isinstance(queue, QueueApi):
                self.add_queue(reference, queue)
            else:
                self.add_queue(reference, None)

    def set_input_queue(
        self, input_queue_reference: QueueReference, input_queue: QueueApi | Any
    ):
        if self.__job_instance.input_queue_reference:
            self.remove_queue(self.__job_instance.input_queue_reference)

        self.__job_instance = replace(
            self.__job_instance, input_queue_reference=input_queue_reference
        )
        if isinstance(input_queue, QueueApi):
            self.add_queue(input_queue_reference, input_queue)
        else:
            self.add_queue(input_queue_reference, None)

    def add_input_queue(
        self, input_queue_reference: QueueReference, input_queue: QueueApi | Any
    ):
        if self.__job_instance.input_queue_reference:
            raise RuntimeError("Input queue already defined")

        return self.set_input_queue(input_queue_reference, input_queue)

    def add_extra_queues(self, extra_queues: dict[QueueReference, Any]):
        if self.__job_instance.extra_queues_references:
            raise RuntimeError("Extra queues already defined")

        return self.set_extra_queues(extra_queues)

    def add_outputs(self, outputs: dict[QueueReference, Any]):
        if self.__job_instance.output_queues_references:
            raise RuntimeError("Outputs already defined")

        return self.set_outputs(outputs)

    def get_kwargs(self, content: JOB_RESULT | JobOutput | None) -> dict[str, Any]:
        kwargs = self.__job_instance.job_definition.kwargs

        content_from_job = (
            content.content if isinstance(content, JobOutput) else content
        )
        output = content_from_job if isinstance(content, JobOutput) else None
        job_output = content if isinstance(content, JobOutput) else None

        if "queues" in self.original_parameters:
            kwargs["queues"] = self.get_extra_queues()
        elif "queue" in self.original_parameters:
            if len(self.get_extra_queues()) > 1:
                raise RuntimeError(
                    "More than one queue defined. Please use queues instead of queue."
                )
            kwargs["queue"] = self.get_extra_queues()[0]

        if "content" in self.original_parameters:
            if content is None:
                self.logger.debug("Content is None")

            kwargs["content"] = content_from_job

        if "output" in self.original_parameters:
            kwargs["output"] = output

        if "job_output" in self.original_parameters:
            kwargs["job_output"] = job_output

        if "api" in self.original_parameters:
            kwargs["api"] = self.dynamic_job_helper_api

        if "parameters" in self.original_parameters:
            kwargs["parameters"] = self.__job_instance.parameters

        if "fself" in self.original_parameters:
            kwargs["fself"] = self.__fself

        if "on_first_run" in self.original_parameters:
            kwargs["on_first_run"] = self.dynamic_job_first_run

        if "checkpoint" in self.original_parameters:
            kwargs["checkpoint"] = self.if_checkpoint

        if "buffer" in self.original_parameters:
            kwargs["buffer"] = self.__buffer

        for parameter in self.original_parameters:
            if parameter in self.__contexts:
                kwargs[parameter] = self.__contexts[parameter]

        return kwargs

    def dynamic_job_first_run(self, *args, **kwargs):
        def wrapper():
            async def inner_wrapper(func: Callable[..., Coroutine[Any, Any, None]]):
                await func(*args, **kwargs)

            return inner_wrapper

        return wrapper

    async def run_original_function(self, *args, **kwargs):
        if kwargs.get("on_first_run") and not self.__had_first_run:
            kwargs["on_first_run"] = kwargs["on_first_run"](*args, **kwargs)

        elif kwargs.get("on_first_run"):
            kwargs["on_first_run"] = lambda: async_lambda(lambda func: None)

        start = time.perf_counter()
        if self.__async_run:
            result = await self.__job_instance.job_definition.run_function(
                *args, **kwargs
            )
        else:
            result = self.__job_instance.job_definition.run_function(*args, **kwargs)
        end = time.perf_counter()

        await self.tc2_time_between_function_execution.observe(end - start)

        self.__had_first_run = True
        return result

    def wrap_result_in_job_output(self, result: Any) -> JobOutput:
        return JobOutput(
            content=result,
            content_parameters={},
            job_content_parameters=[JobContentParameter()],
        )

    def evaluate_job_content_parameters(
        self, job_content_parameters: list[JobContentParameter]
    ):
        for job_content_parameter in job_content_parameters:
            if job_content_parameter.after_send_to_output:
                self.__after_send_to_output.append(
                    job_content_parameter.after_send_to_output
                )

    def prepare_job_output(self, result: Any | JobOutput) -> JobOutput | Any:
        if isinstance(result, JobOutput):
            if not self.__content_job_output_cache:
                return result

            merged = self.merge_job_outputs(self.__content_job_output_cache, result)
            self.evaluate_job_content_parameters(merged.job_content_parameters)
            return merged

        if not self.__job_instance.job_definition.disable_content_wrap:
            output = self.wrap_result_in_job_output(result)

            if not self.__content_job_output_cache:
                return output

            merged = self.merge_job_outputs(self.__content_job_output_cache, output)

            self.evaluate_job_content_parameters(merged.job_content_parameters)

            return merged

        return result

    def merge_job_outputs(self, content: JobOutput, result: JobOutput):
        result = JobOutput(
            content=result.content,
            content_parameters={
                **content.content_parameters,
                **result.content_parameters,
            },
            job_content_parameters=[
                *content.job_content_parameters,
                *result.job_content_parameters,
            ],
        )
        return result

    async def handle_result(
        self, *args, content: JOB_RESULT | JobOutput | None = None, **kwargs
    ) -> Any:
        async def get_result() -> JOB_RESULT:
            return await self.run_original_function(
                *args,
                *self.__job_instance.job_definition.args,
                **kwargs,
                **self.get_kwargs(content=content),
            )

        """
        If function result is a tuple and output is only one queue, then each value of the tuple will be send to the queue as individual events.
        If function result is a tuple and output is a list of queues, then each value of the tuple will be send to the queue with the same index as the output list.
        If function result is not a tuple and output is a list of queues, then the result will be send to each queue.
        If function result is not a tuple and output is only one queue, then the result will be send to the queue.
        """
        self.logger.debug("It will get result")
        result = await get_result()
        self.logger.debug("It got result", result)

        if self.__job_instance.accumulate_write_seconds > 0 and (result or self.get_outputs()):
            result_is_iterable = is_iterable(result)
            result_is_async_iterable = is_async_iterable(result)
            job_inputs = []
            iterated_result = []

            if len(self.__consumed_buffer) > 0:
                job_inputs.extend(self.__consumed_buffer)
                job_inputs.append(content)
                self.__consumed_buffer.clear()

            else:
                job_inputs.append(content)

            if not (result_is_iterable or result_is_async_iterable) and (
                not isinstance(result, tuple)
                or self.__job_instance.job_definition.tuple_result_is_single_value
            ):
                with self.__accumulated_write_items_lock:
                    self.__accumulated_write_items.append((job_inputs[0], result, False))

            else:
                chunk_size = self.__job_instance.job_definition.iterable_chunk_size
                result_has_more_data = True

                while result_has_more_data:
                    result_has_more_data = False

                    if isinstance(result, list):
                        iterated_result = result

                    elif result_is_iterable:
                        iterated_result = []

                        for unique_result in result:
                            iterated_result.append(unique_result)
                            if len(iterated_result) == chunk_size:
                                result_has_more_data = True
                                break
                    
                    elif result_is_async_iterable:
                        iterated_result = []

                        async for unique_result in result:
                            iterated_result.append(unique_result)
                            if len(iterated_result) == chunk_size:
                                result_has_more_data = True
                                break

                    with self.__accumulated_write_items_lock:
                        if len(job_inputs) > 1:
                            if len(iterated_result) != len(job_inputs):
                                if self.__job_instance.job_needs_to_match_input_with_output:
                                    raise RuntimeError(
                                        f"Number of inputs and number of results are different. Tuple results needs to match the number of inputs. Len(job_inputs)={len(job_inputs)}, len(result)={len(iterated_result)}",
                                        job_inputs,
                                        iterated_result,
                                    )

                                else:
                                    # input cannot be matched to output
                                    self.__accumulated_write_items.extend(
                                        [(None, x, False) for i, x in enumerate(iterated_result)]
                                    )
                        
                            else:
                                self.__accumulated_write_items.extend(
                                    [(job_inputs[i], x, False) for i, x in enumerate(iterated_result)]
                                )
                        
                        else:
                            self.__accumulated_write_items.extend(
                                [(job_inputs[0], x, False) for x in iterated_result]
                            )

                return

        outputs = self.get_outputs()
        await self.handle_output(result, outputs)
        await self.handle_after_send_to_output(content, result)

    async def handle_after_send_to_output(
        self, content: JOB_RESULT | JobOutput | None, result: JOB_RESULT
    ):
        if self.__after_send_to_output:
            await asyncio.gather(
                *[
                    func(content, result, self.dynamic_job_helper_api)
                    for func in self.__after_send_to_output
                ]
            )

        self.__after_send_to_output = []

    async def handle_output(
        self,
        result: Any | JobOutput | list[Any | JobOutput],
        outputs: list[QueueApi],
    ) -> Any:
        result_is_iterable = is_iterable(result)
        result_is_async_iterable = is_async_iterable(result)

        if not (result_is_iterable or result_is_async_iterable) and (
            not isinstance(result, tuple)
            or self.__job_instance.job_definition.tuple_result_is_single_value
        ):
            await self.handle_single_output(result, outputs)
        else:
            await self.handle_iterable_output(
                result, result_is_iterable, result_is_async_iterable, outputs
            )

    async def handle_single_output(
        self,
        result: Any | JobOutput,
        outputs: list[QueueApi],
    ) -> Any:
        send_raw = False
        if not outputs:
            outputs = await self.get_output_by_type(type(result))
            send_raw = True

        for output in outputs:
            result_as_job_output = self.prepare_job_output(result)
            result_to_send = result if send_raw else result_as_job_output
            self.logger.debug("it will put", result_to_send, output)
            await asyncio.wait_for(output.put(result_to_send), None)
            await self.tc2_output_counter.inc()
            self.logger.debug("It was put", result_to_send)

    async def handle_iterable_output(
        self,
        result: list[Any | JobOutput],
        result_is_iterable: bool,
        result_is_async_iterable: bool,
        outputs: list[QueueApi],
    ) -> Any:

        if (result_is_iterable or result_is_async_iterable) and len(outputs) == 0:
            outputs = await self.get_output_by_type(type(result[0]))

        if (result_is_iterable or result_is_async_iterable) and len(outputs) == 1:
            if isinstance(result, list):
                await outputs[0].put_iter([self.prepare_job_output(x) for x in result])
                await self.tc2_output_counter.inc(value=len(result))

            elif result_is_async_iterable:
                # FIXME: Duplicated code
                chunks = []
                chunk_size = (
                    self.__job_instance.job_definition.iterable_chunk_size
                    if not self.__job_instance.accumulate_write_seconds
                    else len(result)
                )
                async for unique_result in result:
                    if self.finished_event.is_set():
                        break

                    chunks.append(self.prepare_job_output(unique_result))
                    if len(chunks) == chunk_size:
                        await outputs[0].put_iter(chunks)
                        await self.tc2_output_counter.inc(value=len(chunks))
                        chunks = []
                if chunks:
                    await outputs[0].put_iter(chunks)
                    await self.tc2_output_counter.inc(value=len(chunks))
            else:
                chunks = []
                for unique_result in result:
                    if self.finished_event.is_set():
                        break
                    chunks.append(self.prepare_job_output(unique_result))
                    if len(chunks) == chunk_size:
                        await outputs[0].put_iter(chunks)
                        await self.tc2_output_counter.inc(value=len(chunks))
                        chunks = []
                if chunks:
                    await outputs[0].put_iter(chunks)
                    await self.tc2_output_counter.inc(value=len(chunks))
        elif len(result) != len(outputs) and len(outputs) != 1:
            raise RuntimeError(
                f"Number of outputs and number of results are different. Tuple results needs to match the number of outputs. Len(outputs)={len(outputs)}, len({result})={len(result)}"
            )
        elif len(outputs) == 1:
            for i in range(len(result)):
                await outputs[0].put(self.prepare_job_output(result[i]))
        else:
            for i in range(len(result)):
                await outputs[i].put(self.prepare_job_output(result[i]))

    async def run_defined_job(self, *args, **kwargs):
        content = None

        if not self.metrics_created:
            await self.create_metrics()

        if self.__handle_queue:
            await self.input_queue.wait()
            self.logger.debug("Waiting for content", self.name)

            start = time.perf_counter()

            if len(self.__buffer) == 0:
                self.__buffer.extend(await self.input_queue.get_iter(self.__job_instance.buffer_size or 1))

            await self.tc2_input_counter.inc(len(self.__buffer))

            while len(self.__buffer) > 0:
                content = self.__buffer.pop()
                end = time.perf_counter()

                await self.tc2_time_between_get_content.observe(end - start)

                self.logger.debug("Received content", content)

                if isinstance(content, JobOutput):
                    self.__content_job_output_cache = content

                await self.handle_result(*args, content=content, **kwargs)
                start = time.perf_counter()
            return

        return await self.handle_result(*args, content=content, **kwargs)

    async def managed_run(self):
        self.logger.debug("Running job", self.name)
        if self.__handle_queue and not self.__job_instance.input_queue_reference:
            raise RuntimeError(
                f"Input controller not defined. Cannot handle queue for job {self.name}."
            )

        with ExitStack() as stack:
            self.__contexts = {
                name: stack.enter_context(mgr)
                for name, mgr in (self.__clients_with_context or {}).items()
            }

            return await asyncio.gather(*[
                super().managed_run(),
                self.send_accumulated_data_to_queue()
            ])

    async def graceful_shutdown(self):
        if self.input_queue:
            self.finished_event.set()

    async def on_job_execution_exception(self, exception: Exception):
        print("Exception on job execution", self.__job_instance.job_definition.name)
        print(''.join(traceback.format_exception(exception)))

        self.logger.error("Exception on job execution", exception)
        queues_by_type = await self.dynamic_job_helper_api.central_api.execute(
            GetQueuesByTypeCommand(exception)
        )
        for queue in queues_by_type:
            await queue.put(exception)

    async def get_output_by_type(self, _type: Any):
        if _type in self.__queue_by_type_cache:
            return self.__queue_by_type_cache[_type]

        queues_by_type = await self.dynamic_job_helper_api.central_api.execute(
            GetQueuesByTypeCommand(_type)
        )
        self.__queue_by_type_cache[_type] = queues_by_type
        return queues_by_type

    async def __call__(self, *args, **kwargs):
        return await self.run_original_function(*args, **kwargs)

    def __reduce__(self) -> str | tuple[Any, ...]:
        self.__accumulated_write_items_lock.acquire()

        deserializer = functools.partial(
            DynamicJob.create,
            **{
                "job_instance": self.__job_instance,
                "metrics_client": self.__metrics_client,
                "original_parameters": self.__original_parameters,
                "handle_queue": self.__handle_queue,
                "dynamic_job_helper_api": self.__dynamic_job_helper_api,
                "clients_created": self.__clients_created,
                "contexts": self.__contexts,
                "async_run": self.__async_run,
                "clients_with_context": self.__clients_with_context,
                "central_api": self.central_api,
                "finished_event": (
                    self.finished_event.is_set() if self.finished_event else None
                ),
                "evaluated_queues": self.queue_mapping,
                "on_init": self.__on_init,
                "had_first_run": self.__had_first_run,
                "metrics_created": self.metrics_created,
                "metrics": self.__metrics,
                "pause_event": (
                    self.pause_event.is_set() if self.pause_event else None
                ),
                "accumulated_write_items": self.__accumulated_write_items,
            },
        )

        return deserializer, tuple()

    @classmethod
    def create(cls, **kwargs):
        event = asyncio.Event() if kwargs.get("finished_event") is not None else None
        pause_event = asyncio.Event() if kwargs.get("pause_event") is not None else None

        if kwargs.get("finished_event"):
            event.set()

        if kwargs.get("pause_event"):
            pause_event.set()

        kwargs["finished_event"] = event
        kwargs["pause_event"] = pause_event

        return cls(**kwargs)
