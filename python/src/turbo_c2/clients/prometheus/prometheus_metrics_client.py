from typing import Iterable, Sequence, cast
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Summary,
    start_http_server,
)


class PrometheusMetricsClient:
    def __init__(self, meta: dict[str, str] | None = None):
        self.__registry = CollectorRegistry()
        self.__metrics = {}
        self.__meta = meta or {}

        start_http_server(7475, registry=self.__registry)

    def create_gauge(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str],
        fail_if_exists: bool = True,
    ):
        if self.__metrics.get(name) and fail_if_exists:
            raise ValueError(f"Metric {name} already exists")

        if not self.__metrics.get(name):
            self.__metrics[name] = Gauge(
                name,
                documentation,
                labelnames,
                registry=self.__registry,
            )

    def create_counter(
        self,
        name: str,
        documentation: str,
        labelnames: Sequence[str],
        fail_if_exists: bool = True,
    ):
        if self.__metrics.get(name) and fail_if_exists:
            raise ValueError(f"Metric {name} already exists")

        if not self.__metrics.get(name):
            self.__metrics[name] = Counter(
                name,
                documentation,
                labelnames,
                registry=self.__registry,
            )

    def create_summary(
        self,
        name: str,
        documentation: str,
        labelnames: Sequence[str],
        fail_if_exists: bool = True,
    ):
        
        if self.__metrics.get(name) and fail_if_exists:
            raise ValueError(f"Metric {name} already exists")

        if not self.__metrics.get(name):
            self.__metrics[name] = Summary(
                name,
                documentation,
                labelnames,
                registry=self.__registry,
            )

    def create_histogram(
        self,
        name: str,
        documentation: str,
        labelnames: Sequence[str],
        fail_if_exists: bool = True,
    ):
        if self.__metrics.get(name) and fail_if_exists:
            raise ValueError(f"Metric {name} already exists")

        if not self.__metrics.get(name):
            self.__metrics[name] = Histogram(
                name,
                documentation,
                labelnames,
                registry=self.__registry,
            )

    def set_gauge(self, name: str, value: float, **labels):
        cast(Gauge, self.__metrics[name]).labels(**labels).set(value)

    def inc_gauge(self, name: str, value: float, **labels):
        cast(Gauge, self.__metrics[name]).labels(**labels).inc(value)

    def dec_gauge(self, name: str, value: float, **labels):
        cast(Gauge, self.__metrics[name]).labels(**labels).dec(value)

    def inc_counter(self, name: str, value: float = 1, **labels):
        cast(Counter, self.__metrics[name]).labels(**labels).inc(value)

    def observe_summary(self, name: str, value: float, **labels):
        cast(Summary, self.__metrics[name]).labels(**labels).observe(value)

    def observe_histogram(self, name: str, amount: float, exemplar: dict[str, str] | None = None, **labels):
        cast(Histogram, self.__metrics[name]).labels(**labels).observe(amount, exemplar)
