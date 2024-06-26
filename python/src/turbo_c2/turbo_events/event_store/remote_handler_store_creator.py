from typing import Any, Hashable
import ray
from turbo_c2.turbo_events.commands.handler_store_controller_definition import HandlerStoreControllerDefinition
from turbo_c2.turbo_events.commands.handler_store_type_definition import HandlerStoreTypeDefinition
from turbo_c2.turbo_events.event_store.handler_store_creator import HandlerStoreCreator
from turbo_c2.turbo_events.event_store.remote_handler_store_controller import RemoteHandlerStoreController
from turbo_c2.turbo_events.handlers.handler_controller import (
    HandlerController,
)


class RemoteHandlerStoreCreator(HandlerStoreCreator):
    async def get_controller(
        self, controller_id: Hashable | None
    ) -> RemoteHandlerStoreController:
        if not controller_id:
            return (
                await self.central_api.execute(HandlerStoreControllerDefinition.get())
            )[0]
        return await self.central_api.execute(
            HandlerStoreControllerDefinition.get(controller_id)
        )

    async def get_type(self, type_id: str | None, definition_hash: Hashable):
        if not type_id:
            type_by_hash = await self.central_api.execute(
                HandlerStoreTypeDefinition.get(definition_hash)
            )

            if not type_by_hash:
                return (await self.central_api.execute(HandlerStoreTypeDefinition.get()))[
                    0
                ]

            return type_by_hash
        return await self.central_api.execute(HandlerStoreTypeDefinition.get(type_id))

    async def create(
        self, handlers: list[HandlerController], meta: dict[str, Any] | None = None
    ):
        controller = await self.get_controller(meta.get("handler_store_controller_id", None))

        event_store_type = await self.get_type(
            meta.get("handler_store_type_id", None), HandlerController
        )

        return controller(ray.remote(event_store_type).options(name=self.identifier, lifetime="detached", memory=100 * 1024 * 1024, scheduling_strategy="SPREAD").remote(handlers)) # type: ignore
