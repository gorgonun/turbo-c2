from collections import deque
from typing import Any, Callable, Coroutine, Tuple
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import (
    PrometheusMetricsApi,
)
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.helpers.turbo_logger import TurboLogger
from turbo_c2.interfaces.queue_api import QueueApi


class BufferContext:
    def __init__(self, buffer: deque, after_consume_buffer: Callable[[], None]):
        self.buffer = buffer
        self.after_consume_buffer = after_consume_buffer

    def __enter__(self):
        self.after_consume_buffer(self.buffer)
        return self.buffer
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.buffer.clear()


class DynamicJobHelperApi:
    def __init__(
        self,
        input_queue_data: Tuple[QueueReference, QueueApi],
        queues: dict[QueueReference, QueueApi],
        outputs: dict[QueueReference, QueueApi] | None,
        central_api: DefaultCentralApi,
        logger: TurboLogger,
        metrics_api: PrometheusMetricsApi,
        job_instance: JobInstance,
        send_to_self_function: Callable[[Any], Coroutine[Any, Any, None]],
        buffer: deque,
        after_consume_buffer: Callable[[], None],
    ) -> None:
        self.queues = {
            **queues,
            **(outputs or {}),
            input_queue_data[0]: input_queue_data[1],
        }
        self.__input_queue = input_queue_data[1]
        self.__output_queues = outputs or {}
        self.__central_api = central_api
        self.__logger = logger
        self.__metrics_api = metrics_api
        self.__job_instance = job_instance
        self.__send_to_self_function = send_to_self_function
        self.__buffer = buffer
        self.__after_consume_buffer = after_consume_buffer

    @property
    def central_api(self):
        return self.__central_api

    @property
    def logger(self):
        return self.__logger

    @property
    def metrics_api(self):
        return self.__metrics_api
    
    @property
    def job_instance(self):
        return self.__job_instance
    
    @property
    def input_queue(self):
        return self.__input_queue
    
    @property
    def output_queues(self):
        return self.__output_queues

    async def send_to_queue(self, data, queue_reference: QueueReference | None = None):
        if not queue_reference and len(self.queues) > 1:
            raise RuntimeError(
                "More than one queue defined. Please provide queue_reference."
            )

        queue = self.queues[queue_reference or list(self.queues.keys())[0]]
        await queue.put(data)

    async def send_to_self(self, data):
        return await self.__send_to_self_function(data)
    
    def buffer_context(self):
        return BufferContext(self.__buffer, self.__after_consume_buffer)
