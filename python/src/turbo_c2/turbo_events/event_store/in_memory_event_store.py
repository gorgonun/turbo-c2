from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, thread
from dataclasses import dataclass, field
import datetime
import threading
import time
from typing import Any, Set, Union, cast
import uuid
from turbo_c2.helpers.event_utils import EventUtils
from turbo_c2.turbo_events.domain.handler_after_execution_property_enum import (
    HandlerAfterExecutionPropertyEnum,
)
from turbo_c2.turbo_events.events.empty_element import EmptyElement
from turbo_c2.helpers.kv_cursor_utils import (
    delete_resource_from_path,
    get_all_elements,
    get_all_matching_elements,
    put_resource,
)
from turbo_c2.helpers.date_time import DateTime
from turbo_c2.turbo_events.event_store.event_store import EventStore
from turbo_c2.turbo_events.handlers.handler_controller import (
    HandlerController,
)
from turbo_c2.turbo_events.operators.event_operators import Operation
from turbo_c2.turbo_events.events.event_reference import EventReference
from turbo_c2.turbo_events.interfaces.handler import Handler
from turbo_c2.helpers.lock_provider import LockProvider
from turbo_c2.turbo_events.events.event import Event


MappingData = dict[
    str,
    dict[Any, Union["MappingData", list[Handler[Operation]]]]
    | list[Handler[Operation]],
]


@dataclass
class EventMapping:
    data: MappingData = field(default_factory=lambda: {})
    meta: dict[str, set[str]] = field(default_factory=lambda: {})


class InMemoryEventStore(EventStore):
    date_time: DateTime = DateTime()
    lock_provider = LockProvider()

    def __init__(
        self,
        identifier: str | None = None,
    ) -> None:
        self.event_store = {}
        super().__init__(identifier=identifier or uuid.uuid4().hex)
        self.event_store_lock = threading.Lock()
        self.__events_to_be_put = {}
        self.__finished = threading.Event()
        self.__has_events_to_put = threading.Event()
        self.__event_reference_cache = {}

    def get_event_type_cache_lock(self, event_type: str):
        lock = self.__event_reference_cache.setdefault(event_type, {"cache": {}, "lock": threading.Lock()})["lock"]
        return lock
    
    def get_event_reference_cache_data(self, event_reference: EventReference) -> Set[Event] | False | None:
        with self.get_event_type_cache_lock(event_reference.event_type):
            return self.__event_reference_cache[event_reference.event_type]["cache"].get(event_reference)
    
    def clear_cache_for_type(self, event_type: str):
        with self.get_event_type_cache_lock(event_type):
            self.__event_reference_cache[event_type]["cache"].clear()

    def put_cache_for_reference(self, event_reference: EventReference, data: Set[Event] | False):
        with self.get_event_type_cache_lock(event_reference.event_type):
            self.__event_reference_cache[event_reference.event_type]["cache"][event_reference] = data

    def put_event(
        self, event: Event, acquire_lock: bool = True, fail_if_locked: bool = False
    ) -> str | None:
        req = uuid.uuid4().hex
        self.__events_to_be_put[req] = (event, threading.Event())
        self.__has_events_to_put.set()
        return req
    
    def put_events(self, events: list[Event], acquire_lock: bool = True, fail_if_locked: bool = False) -> list[str | None]:
        req = uuid.uuid4().hex
        self.__events_to_be_put[req] = (events, threading.Event())
        self.__has_events_to_put.set()

        return req
    
    def run(self):
        while True:
            if self.__finished.is_set():
                break

            self.__has_events_to_put.wait()

            reqs = list(self.__events_to_be_put.keys())
            if not reqs:
                self.__has_events_to_put.clear()

            for req in reqs:
                events = self.__events_to_be_put[req][0]
                req_event: threading.Event = self.__events_to_be_put[req][1]

                for event in events:
                    for (key, value) in event.tuples():
                        self.event_store.setdefault(event.get_type(), {}).setdefault(key, {}).setdefault(value, set()).add(event)

                    self.clear_cache_for_type(event.get_type())

                req_event.set()
                del self.__events_to_be_put[req]

    def graceful_shutdown(self):
        self.__finished.set()

    def is_request_finished(self, req: str):
        if req not in self.__events_to_be_put:
            return True

        self.__events_to_be_put[req][1].wait()
        return True

    def event_happened(self, event_reference: EventReference):
        result = set()

        sorted_references = sorted(event_reference.tuples(), key=lambda x: 1 if x[1] == EmptyElement else 0)

        for (key, value) in sorted_references:
            keys = self.event_store.get(event_reference.event_type, {}).get(key, {})

            # List left empty elements to the end. Because of that, we only needs to keep iterating if result is empty, as the empty elements will get all elements.
            if value == EmptyElement:
                if result:
                    break
                found_events = list(keys.values())
            else:
                found_events = [keys[value]] if keys.get(value) else []

            if not found_events:
                return False
            
            for found_event in found_events:
                if result:
                  result.intersection_update(found_event)
                else:
                    result.update(found_event)

        return list(result)
    
    def events_happened(self, event_references: list[EventReference]):
        def get_event_with_cache(result_acc: dict[Event, list[Event] | False], event_reference: EventReference):
            result_from_cache = self.get_event_reference_cache_data(event_reference)

            if result_from_cache is None:
                result = self.event_happened(event_reference)
                self.put_cache_for_reference(event_reference, result)
            
            result_acc[event_reference] = result_from_cache if result_from_cache is not None else result

        before_cache = time.perf_counter()
        result_acc = {}

        with ThreadPoolExecutor() as executor:
            list(executor.map(lambda event: get_event_with_cache(result_acc, event), event_references))


        after_cache = time.perf_counter()
        return result_acc
