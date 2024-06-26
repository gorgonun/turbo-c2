from typing import Any, Hashable
import ray
from turbo_c2.extra_api.command.queue.get_queue_api_command import GetQueueApiCommand
from turbo_c2.extra_api.command.queue.get_queue_apis_command import GetQueueApisCommand
from turbo_c2.extra_api.command.queue.get_queue_controller_command import (
    GetQueueControllerCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_controllers_command import (
    GetQueueControllersCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_type_command import GetQueueTypeCommand
from turbo_c2.extra_api.command.queue.get_queue_types_command import GetQueueTypesCommand
from turbo_c2.queues.queue_creator import QueueCreator
from turbo_c2.queues.queue_definition import QueueDefinition


class RemoteQueueCreator(QueueCreator):
    async def get_queue_controller(self, queue_controller_id: Hashable | None):
        if not queue_controller_id:
            return (await self.central_api.execute(GetQueueControllersCommand()))[0]
        return await self.central_api.execute(
            GetQueueControllerCommand(queue_controller_id)
        )

    async def get_queue_api(self, queue_api_id: Hashable | None):
        if not queue_api_id:
            return (await self.central_api.execute(GetQueueApisCommand()))[0]
        return await self.central_api.execute(GetQueueApiCommand(queue_api_id))

    async def get_queue_type(
        self, queue_type_id: str | None, queue_definition_hash: Hashable
    ):
        if not queue_type_id:
            type_by_hash = await self.central_api.execute(
                GetQueueTypeCommand(queue_definition_hash=queue_definition_hash)
            )

            if not type_by_hash:
                return (await self.central_api.execute(GetQueueTypesCommand()))[0]

            return type_by_hash
        return await self.central_api.execute(GetQueueTypeCommand(queue_type_id))

    async def create(
        self, definition: QueueDefinition, meta: dict[str, Any] | None = None
    ):
        self.logger.debug("Creating new queue", definition.name)

        queue_controller = await self.get_queue_controller(
            meta.get("queue_controller_id", definition.meta.get("queue_controller_id"))
        )
        queue_api = await self.get_queue_api(
            meta.get("queue_api_id", definition.meta.get("queue_api_id"))
        )

        queue_type = await self.get_queue_type(
            meta.get("queue_type_id", definition.meta.get("queue_type_id")),
            type(definition),
        )

        self.logger.info("Creating queue with type", queue_type)

        queue = queue_type(definition)

        prometheus_client_actor_definition = (
            await self.central_api.get_object_reference(
                ["resource_creator", "actor", "metrics", "client", "prometheus"]
            )
        )

        if not prometheus_client_actor_definition:
            raise RuntimeError("Prometheus client actor not found")

        metrics_client = prometheus_client_actor_definition.actor_ref

        return queue_api(ray.remote(queue_controller).options(num_cpus=0.1, memory=100 * 1024 * 1024, name=definition.name, lifetime="detached", scheduling_strategy="SPREAD").remote(queue, queue_definition=definition, metrics_client=metrics_client))  # type: ignore
