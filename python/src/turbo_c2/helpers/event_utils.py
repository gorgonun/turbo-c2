import contextlib
from dataclasses import dataclass
import asyncio
from typing import Any, Coroutine


@dataclass
class CombinedEvents():
    events: dict[str, asyncio.Event | None]
    change_condition = asyncio.Event()
    create_missing_events = True

    def __post_init__(self):
        if self.create_missing_events:
            for key, value in self.events.items():
                if value is None:
                    self.events[key] = asyncio.Event()

    @property
    def defined_events(self):
        for event in self.events.values():
            if event is None:
                raise RuntimeError("Some events are not defined.", self.events)
            yield event

    def get(self, key: str, default: Any = None) -> asyncio.Event | None:
        return self.events.get(key, default)

    def __getitem__(self, key: str) -> asyncio.Event:
        return self.events[key]
    
    def __setitem__(self, key: str, value: asyncio.Event | None):
        self.events[key] = value

    def set_event(self, event_name: str):
        if self.events[event_name] is None:
            raise RuntimeError(f"Event {event_name} is not defined.")
        self.events[event_name].set()
        self.notify_change()

    def notify_change(self):
        self.change_condition.set()

    def is_any_set(self):
        return any(event.is_set() for event in self.defined_events)

    async def wait_any_set(self, timeout: int | None = None):
        async def wrapped():
            while self.is_any_set() is False:
                await self.change_condition.wait()
                self.change_condition.clear()
        return await EventUtils.safe_wait_for(wrapped(), timeout=timeout)

    # FIXME: This is not working as expected
    # async def wait_all_set(self, timeout: int | None = None):
    #     start_time = datetime.datetime.now()
    #     limit_time = start_time + datetime.timedelta(seconds=timeout) if timeout else None
    #     while not all(event.is_set() for event in self.defined_events):
    #         if limit_time and datetime.datetime.now() > limit_time:
    #             return
    #         self.change_condition.wait(timeout)


class EventUtils:
    @classmethod
    def serialize_event(cls, event: asyncio.Event) -> bool:
        return event.is_set()
    
    @classmethod
    def deserialize_event(cls, event: bool) -> asyncio.Event:
        new_event = asyncio.Event()
        if event:
            new_event.set()
        return new_event
    
    @classmethod
    def combine_events(self, events: dict[str, asyncio.Event]):
        return CombinedEvents(events)
    
    @classmethod
    async def safe_wait_for(cls, c_routine: Coroutine, timeout: int | None = None):
        with contextlib.suppress(asyncio.TimeoutError, asyncio.CancelledError):
            return await asyncio.wait_for(c_routine, timeout=timeout)
