from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
import datetime
import time
from typing import Any, Union, cast
import uuid
from turbo_c2.helpers.event_utils import EventUtils
from turbo_c2.turbo_events.domain.handler_after_execution_property_enum import (
    HandlerAfterExecutionPropertyEnum,
)
from turbo_c2.turbo_events.event_store.handler_store import HandlerStore
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


class InMemoryHandlerStore(HandlerStore):
    date_time: DateTime = DateTime()
    lock_provider = LockProvider()

    def __init__(
        self,
        handlers: list[HandlerController[Handler[Operation]]],
        identifier: str | None = None,
    ) -> None:
        self.rule_mapping = self.map_rules(handlers)
        # { session: { "mapping" : {}, "handlers": { handler: ("path", { "id": handler} )}, "lock": Lock(), "reserved_time": datetime.datetime }}
        self.session_data = {}
        super().__init__(identifier=identifier or uuid.uuid4().hex)
        self.session_data_lock = asyncio.Lock()

    def register_handler(
        self, controller: HandlerController[Handler[Operation]]
    ) -> None:
        self.rule_mapping = self.map_rules([controller], self.rule_mapping)

    def register_handlers(
        self, controllers: list[HandlerController[Handler[Operation]]]
    ) -> None:
        self.rule_mapping = self.map_rules(controllers, self.rule_mapping)

    def unlock(self, session: str):
        if session in self.session_data:
            self.session_data[session]["lock"].release()
            del self.session_data[session]

    async def set_lock_for_event(self, event: Event, time_mills: int | None):
        until = (
            None
            if time_mills is None
            else self.date_time.now() + datetime.timedelta(milliseconds=time_mills)
        )
        session = uuid.uuid4().hex
        mapping = self.map_rules(self.__get_handler_by_last_event(event)[0])
        lock = self.lock_provider.get_lock()
        await lock.acquire()

        self.session_data[session] = {
            "mapping": mapping,
            "lock": lock,
            "reserved_time": until,
        }

        return session

    async def get_lock(self, event: Event, fail_if_locked: bool = False) -> str | None:
        async with self.session_data_lock:
            session, session_data = await self.get_session_lock_for_event(event)
            if session:
                lock: asyncio.Lock = session_data["lock"]
                reserved_time = session_data["reserved_time"]

                if reserved_time and reserved_time < self.date_time.now():
                    self.unlock(session)
                    return await self.set_lock_for_event(event, 6000)

                if fail_if_locked:
                    raise RuntimeError(f"Event {event} is already locked.")

                await EventUtils.safe_wait_for(
                    lock.acquire(),
                    (
                        (self.date_time.now() - reserved_time).total_seconds()
                        if reserved_time
                        else None
                    ),
                )

                if lock.locked():
                    return None

        return await self.set_lock_for_event(event, 6000)

    async def get_session_lock_for_event(self, event: Event):
        async def __get_result_with_session_name(session_name: str):
            if not self.session_data.get(session_name, {}).get("mapping"):
                return False, session_name, None

            return (
                await self.is_event_locked(
                    event,
                    self.session_data[session_name]["mapping"][event.get_type()].data,
                ),
                session_name,
                self.session_data[session_name]
            )

        if not self.session_data:
            return None, None

        
        session_result_with_name = await asyncio.gather(
            *[
                __get_result_with_session_name(session_name)
                for session_name in self.session_data.keys()
            ]
        )

        for result, session_name, session in session_result_with_name:
            if result:
                return session_name, session
            
        return None, None

    async def is_event_locked(self, event: Event, session_mapping: dict) -> bool:
        return bool(self.__get_handler_by_last_event(event, session_mapping)[0])

    async def on_execution(
        self,
        evaluation_result: bool,
        controller: HandlerController[Handler[Operation]],
        session: str,
    ):
        after_execution_property = (
            controller.properties.after_true
            if evaluation_result
            else controller.properties.after_false
        )

        if after_execution_property == HandlerAfterExecutionPropertyEnum.DELETE:
            for event in controller.handler.when.references:
                delete_resource_from_path(
                    self.rule_mapping[event.event_type].data,
                    event.tuples(),
                    controller.handler.when,
                )

    def map_rules(
        self,
        handlers: list[HandlerController[Handler[Operation]]],
        rules: dict[str, EventMapping] = None,
    ):
        # event_type -> {data, meta} -> {identification} -> [handlers]
        rules = rules if rules is not None else {}

        for handler in handlers:
            for event in handler.handler.when.references:
                event_type_mapping = rules.setdefault(event.event_type, EventMapping())

                cursor = cast(
                    dict[str, dict[Any, list[Handler[Operation]]]]
                    | list[Handler[Operation]],
                    event_type_mapping.data,
                )
                reference_list = event.tuples()

                for i, reference in enumerate(reference_list):
                    cursor = cast(
                        dict[str, dict[Any, list[Handler[Operation]]]]
                        | list[Handler[Operation]],
                        cursor,
                    )

                    if isinstance(cursor, list):
                        raise RuntimeError(
                            "One reference does not have a key (parameter name) and value (parameter value)."
                        )

                    event_type_mapping.meta.setdefault(
                        "referenced_parameters", set()
                    ).add(reference[0])

                    if i == len(reference_list) - 1:
                        cursor[reference[0]] = cursor.get(reference[0], {})
                        cursor[reference[0]].setdefault(reference[1], {}).update(
                            {handler.handler.when: handler}
                        )
                        break

                    else:
                        cursor = cast(
                            dict[Any, list[Handler[Operation]]],
                            cursor.setdefault(reference[0], {}),
                        )
                        cursor = cursor.setdefault(reference[1], {})

        return rules

    def __get_handler_by_last_event(
        self,
        event: Event,
        mapping: dict | None = None,
        cache: dict | None = None,
    ) -> list[HandlerController[Handler[Operation]]]:
        mapping = mapping or getattr(
            self.rule_mapping.get(event.get_type()), "data", None
        )

        if not mapping:
            return []

        identificator_data = list(filter(None, event.reference.get_identification_data() or []))

        handlers_by_identification_key = get_all_matching_elements(
            mapping,
            identificator_data,
            skip_last_generic=True,
            generic_element=EmptyElement,
        )

        handler_by_not_identifiable_event = get_all_matching_elements(
            mapping, event.tuples(), generic_element=EmptyElement
        )

        result = []

        for path, value in [
            *handlers_by_identification_key,
            *handler_by_not_identifiable_event,
        ]:
            if value:
                result.extend(value.values())

        return result

    async def get_handler_by_last_event(self, event: Event, session: str | None):
        if not session:
            return self.__get_handler_by_last_event(event)

        async with self.session_data_lock:
            current_locked_session, session_data = await self.get_session_lock_for_event(event)

        if current_locked_session != session:
            # FIXME: lock not required for now
            # print("//////////////////////////////", event, self.session_data)
            print(f"Got session {session}, but expected {current_locked_session}.")
            # raise RuntimeError(
            #     f"Got session {session}, but expected {current_locked_session}."
            # )

        return self.__get_handler_by_last_event(
            event, cache=session_data.setdefault("handlers", {})
        )
    
    async def get_handler_by_last_events(self, events_with_session: list[tuple[str | None, Event]]):
        async def __get_handler_by_last_event(event: Event, session: str | None):
            return (event, await self.get_handler_by_last_event(event, session))

        return await asyncio.gather(
            *[
                __get_handler_by_last_event(event, session)
                for session, event in events_with_session
            ]
        )

    async def get_handler_by_event_type(
        self, event_type: str
    ) -> list[HandlerController[Handler[Operation]]]:

        if self.rule_mapping.get(event_type):

            result_by_id = get_all_elements(
                self.rule_mapping[event_type].data,
                ["id"],
                skip_values=set([EmptyElement]),
            )
            result_by_generic = get_all_elements(
                self.rule_mapping[event_type].data,
                list(self.rule_mapping[event_type].meta["referenced_parameters"]),
                get_values=lambda key, value: EmptyElement if key == "id" else value,
            )

            return list({**result_by_id, **result_by_generic}.values())

        return []
