import asyncio
from typing import Any, TypeVar
from turbo_c2.helpers.event_utils import EventUtils
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import Counter, Gauge, PrometheusMetricsApi
from turbo_c2.queues.ebf_queue import EBFQueue

from turbo_c2.queues.queue_controller import QueueController

from turbo_c2.queues.queue_definition import QueueDefinition


# Remote queue reference
T = TypeVar("T", bound=EBFQueue)


class RemoteQueueController(QueueController[T]):
    def __init__(
        self,
        queue: T,
        queue_definition: QueueDefinition,
        name: str | None = None,
        strict_consumers: list[str] | None = None,
        wait_data_event: asyncio.Event | None = None,
        finished_event: asyncio.Event | None = None,
        metrics_client: PrometheusMetricsApi | None = None,
        metrics_created: bool = False,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        if not queue:
            raise RuntimeError("queue is None")

        super().__init__(
            queue,
            name=name,
            queue_definition=queue_definition,
            strict_consumers=strict_consumers,
            wait_data_event=wait_data_event,
            finished_event=finished_event,
        )

        self.__metrics_client = metrics_client
        self.metrics_created = metrics_created
        self.__metrics = metrics or {}

    @property
    def tc2_queue_content(self) -> Gauge:
        metric = self.__metrics.get("tc2_queue_content")

        if not metric:
            raise ValueError("Metric not found")

        return metric
    
    @property
    def tc2_queue_content_hist(self) -> Counter:
        metric = self.__metrics.get("tc2_queue_content_hist")

        if not metric:
            raise ValueError("Metric not found")

        return metric

    async def create_metric(self):
        self.__metrics["tc2_queue_content"] = await self.__metrics_client.gauge(
            "tc2_queue_content",
            "Content inside queue",
            labels={"queue_name": self.queue_name}
        )

        self.__metrics["tc2_queue_content_hist"] = await self.__metrics_client.counter(
            "tc2_queue_content_hist",
            "Content inside queue",
            labels={"queue_name": self.queue_name}
        )

    def get_queue_name(self) -> str:
        return self.queue_name

    def get_queue(self) -> T:
        return self.queue

    def get_name(self) -> str:
        return self.name

    def get_strict_consumers(self) -> set[str]:
        return self.strict_consumers

    async def put_data(self, data: T) -> None:
        if not self.metrics_created:
            await self.create_metric()
            self.metrics_created = True

        result = await self.queue.put(data)  # type: ignore
        self.set_wait_data_event()
        await self.tc2_queue_content.set(await self.qsize())
        await self.tc2_queue_content_hist.inc()
        return result
    
    async def put_data_iter(self, data: list[T]) -> None:
        if not self.metrics_created:
            await self.create_metric()
            self.metrics_created = True

        result = await self.queue.put_iter(data)
        self.set_wait_data_event()
        await self.tc2_queue_content.set(await self.qsize())
        await self.tc2_queue_content_hist.inc(len(data))
        return result

    async def get_data(self) -> T:
        result = await self.queue.get()  # type: ignore
        await self.tc2_queue_content.set(await self.qsize())
        return result
    
    async def get_data_iter(self, count: int) -> list[T]:
        result = await self.queue.get_iter(count)
        await self.tc2_queue_content.set(await self.qsize())
        return result

    async def qsize(self) -> int:
        return await self.queue.qsize()  # type: ignore

    def __reduce__(self) -> str | tuple[Any, ...]:
        deserializer = RemoteQueueController.create
        serialized_data = (
            self.queue,
            self.name,
            self.strict_consumers,
            EventUtils.serialize_event(self.wait_data_event)
            if self.wait_data_event
            else None,
            EventUtils.serialize_event(self.finished_event)
            if self.finished_event
            else None,
            self.metrics_created,
            self.__metrics,
        )
        return deserializer, serialized_data

    @classmethod
    def create(
        cls,
        queue: T,
        name: str | None = None,
        strict_consumers: list[str] | None = None,
        wait_data: bool | None = None,
        finished: bool | None = None,
        metrics_created: bool | None = None,
        metrics: dict[str, Any] | None = None,
    ):
        wait_data_event = (
            EventUtils.deserialize_event(wait_data) if wait_data is not None else None
        )
        finished_event = (
            EventUtils.deserialize_event(finished) if finished is not None else None
        )

        return cls(
            queue,
            name,
            strict_consumers,
            wait_data_event=wait_data_event,
            finished_event=finished_event,
            metrics_created=metrics_created,
            metrics=metrics,
        )

    async def wait(self, timeout: int | None = None):
        return await super().wait(timeout)
