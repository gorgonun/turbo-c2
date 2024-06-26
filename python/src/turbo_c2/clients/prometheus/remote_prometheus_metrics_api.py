from typing import Any, Iterable
from turbo_c2.clients.prometheus.prometheus_metrics_client import PrometheusMetricsClient
from turbo_c2.interfaces.clients.prometheus.prometheus_metrics_api import Counter, Gauge, Histogram, PrometheusMetricsApi


class OptionalLabels:
    def __init__(self, labelnames: Iterable[str] | None, labels: dict[Any, Any] | None):
        self.labelnames = labelnames or set()
        self.labels = labels or {}
        
    def verify_labels(self, labels: dict[Any, Any]):
        if not self.labelnames == set(labels.keys()):
            raise ValueError("labels do not match labelnames")


class RemoteCounter(Counter, OptionalLabels):
    def __init__(
        self,
        prometheus_client: PrometheusMetricsClient,
        name: str,
        documentation: str,
        labelnames: set[str] | None = None,
        labels: dict[Any, Any] | None = None,
    ):
        self.prometheus_client = prometheus_client
        self.name = name
        self.documentation = documentation
        super().__init__(labelnames, labels)

    async def inc(self, value: float = 1, **labels):
        inc_labels = {**labels, **self.labels}

        self.verify_labels(inc_labels)

        await self.prometheus_client.inc_counter.remote(
            self.name, value, **inc_labels)
        

class RemoteGauge(Gauge, OptionalLabels):
    def __init__(
        self,
        prometheus_client: PrometheusMetricsClient,
        name: str,
        documentation: str,
        labelnames: set[str] | None = None,
        labels: dict[Any, Any] | None = None,
    ):
        self.prometheus_client = prometheus_client
        self.name = name
        self.documentation = documentation
        super().__init__(labelnames, labels)

    async def set(self, value: float = 1, **labels):
        set_labels = {**labels, **self.labels}

        self.verify_labels(set_labels)

        await self.prometheus_client.set_gauge.remote(
            self.name, value, **set_labels)
    
    async def inc(self, value: float = 1, **labels):
        inc_labels = {**labels, **self.labels}

        self.verify_labels(inc_labels)

        await self.prometheus_client.inc_gauge.remote(
            self.name, value, **inc_labels)
        
    async def dec(self, value: float = 1, **labels):
        dec_labels = {**labels, **self.labels}

        self.verify_labels(dec_labels)

        await self.prometheus_client.dec_gauge.remote(
            self.name, value, **dec_labels)
        

class RemoteHistogram(Histogram, OptionalLabels):
    def __init__(
        self,
        prometheus_client: PrometheusMetricsClient,
        name: str,
        documentation: str,
        labelnames: set[str] | None = None,
        labels: dict[Any, Any] | None = None,
    ):
        self.prometheus_client = prometheus_client
        self.name = name
        self.documentation = documentation
        super().__init__(labelnames, labels)

    async def observe(self, amount: float, exemplar: dict[str, str] | None = None, **labels):
        inc_labels = {**labels, **self.labels}

        self.verify_labels(inc_labels)

        await self.prometheus_client.observe_histogram.remote(
            self.name, amount, exemplar, **inc_labels)


class RemotePrometheusMetricsApi(PrometheusMetricsApi):

    def __init__(self, prometheus_client: PrometheusMetricsClient):
        self.prometheus_client = prometheus_client

    async def counter(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ):
        client_label_names = self.get_client_labels(labelnames, labels)

        await self.prometheus_client.create_counter.remote(
            name, documentation, client_label_names, fail_if_exists, **kwargs
        )

        counter = RemoteCounter(
            self.prometheus_client,
            name,
            documentation,
            client_label_names,
            labels,
        )

        return counter
    
    async def gauge(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ):
        client_label_names = self.get_client_labels(labelnames, labels)

        await self.prometheus_client.create_gauge.remote(
            name, documentation, client_label_names, fail_if_exists, **kwargs
        )

        gauge = RemoteGauge(
            self.prometheus_client,
            name,
            documentation,
            client_label_names,
            labels,
        )

        return gauge
    
    async def histogram(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str] | None = None,
        labels: dict[Any, Any] | None = None,
        fail_if_exists: bool = False,
        **kwargs
    ):
        client_label_names = self.get_client_labels(labelnames, labels)

        await self.prometheus_client.create_histogram.remote(
            name, documentation, client_label_names, fail_if_exists, **kwargs
        )

        histogram = RemoteHistogram(
            self.prometheus_client,
            name,
            documentation,
            client_label_names,
            labels,
        )

        return histogram

    @staticmethod
    def get_client_labels(labelnames: Iterable[str], labels: dict[Any, Any]) -> set[Any]:
        client_label_names = set(labelnames or [])

        if labels:
            names_from_labels = set(labels.keys())
            client_label_names.update(names_from_labels)

        return client_label_names
