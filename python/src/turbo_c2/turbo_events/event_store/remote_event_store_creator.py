from typing import Any, Hashable
import ray
from turbo_c2.domain.scheduler.waitable_item import WaitableItem
from turbo_c2.extra_api.command.queue.get_queues_by_type_command import GetQueuesByTypeCommand
from turbo_c2.turbo_events.commands.event_store_controller_definition import (
    EventStoreControllerDefinition,
)
from turbo_c2.turbo_events.commands.event_store_type_definition import (
    EventStoreTypeDefinition,
)
from turbo_c2.turbo_events.event_store.event_store_creator import (
    EventStoreCreator,
)
from turbo_c2.turbo_events.handlers.handler_controller import (
    HandlerController,
)
from turbo_c2.turbo_events.event_store.remote_event_store_controller import (
    RemoteEventStoreController,
)


class RemoteEventStoreCreator(EventStoreCreator):
    async def get_controller(
        self, controller_id: Hashable | None
    ) -> RemoteEventStoreController:
        if not controller_id:
            return (
                await self.central_api.execute(EventStoreControllerDefinition.get())
            )[0]
        return await self.central_api.execute(
            EventStoreControllerDefinition.get(controller_id)
        )

    async def get_type(self, type_id: str | None, definition_hash: Hashable):
        if not type_id:
            type_by_hash = await self.central_api.execute(
                EventStoreTypeDefinition.get(definition_hash)
            )

            if not type_by_hash:
                return (await self.central_api.execute(EventStoreTypeDefinition.get()))[
                    0
                ]

            return type_by_hash
        return await self.central_api.execute(EventStoreTypeDefinition.get(type_id))

    async def create(
        self, definition, meta: dict[str, Any] | None = None
    ):
        controller = await self.get_controller(meta.get("event_store_controller_id", None))

        event_store_type = await self.get_type(
            meta.get("event_store_type_id", None), HandlerController
        )

        waitable_queue = await self.central_api.execute(
            GetQueuesByTypeCommand(WaitableItem)
        )

        if not waitable_queue:
            raise Exception("No waitable queue found")

        result = controller(ray.remote(event_store_type).options(name=self.identifier, lifetime="detached", memory=250 * 1024 * 1024, scheduling_strategy="SPREAD", max_concurrency=1000).remote()) # type: ignore

        for queue in waitable_queue:
            await queue.put(WaitableItem(result.run, result.graceful_shutdown,"event_store_put_events"))

        return result
