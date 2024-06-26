import abc
from typing import Any, Iterable
from turbo_c2.clients.prometheus.prometheus_metrics_client import PrometheusMetricsClient


class Counter(abc.ABC):
    @abc.abstractmethod
    async def inc(self, value: float = 1, **labels):
        pass
        

class Gauge(abc.ABC):
    @abc.abstractmethod
    async def set(self, value: float = 1, **labels):
        pass
    
    @abc.abstractmethod
    async def inc(self, value: float = 1, **labels):
        pass
        
    @abc.abstractmethod
    async def dec(self, value: float = 1, **labels):
        pass

class Histogram(abc.ABC):
    @abc.abstractmethod
    async def observe(self, amount: float, exemplar: dict[str, str] | None = None, **labels):
        pass


class PrometheusMetricsApi(abc.ABC):
    @abc.abstractmethod
    def __init__(self, prometheus_client: PrometheusMetricsClient):
        pass

    @abc.abstractmethod
    async def counter(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ) -> Counter:
        pass
    
    @abc.abstractmethod
    async def gauge(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ) -> Gauge:
        pass

    @abc.abstractmethod
    async def histogram(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ):
        pass
