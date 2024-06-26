from dataclasses import dataclass
import requests

from turbo_c2.interfaces.client import Client


class PrometheusHttpClient(Client):
    @dataclass
    class InstantQuery:
        query: str
        time: str | None = None
        timeout: str | None = None

    @dataclass
    class RangeQuery:
        query: str
        start: str
        end: str
        step: str
        timeout: str | None = None

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def query_instant(
        self, query: str, time: str | None = None, timeout: str | None = None
    ):
        url = f"{self.host}:{self.port}/api/v1/query"
        params = {"query": query, "time": time, "timeout": timeout}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def query_range(
        self, query: str, start: str, end: str, step: str, timeout: str | None = None
    ):
        url = f"{self.host}:{self.port}/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step,
            "timeout": timeout,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def query(self, query_obj: InstantQuery | RangeQuery):
        if isinstance(query_obj, self.InstantQuery):
            return self.query_instant(
                query_obj.query, query_obj.time, query_obj.timeout
            )

        elif isinstance(query_obj, self.RangeQuery):
            return self.query_range(
                query_obj.query,
                query_obj.start,
                query_obj.end,
                query_obj.step,
                query_obj.timeout,
            )
        
        else:
            raise ValueError(f"Invalid query object {query_obj}")
