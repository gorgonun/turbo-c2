from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.queues.local_queue_controller import LocalQueueController
from turbo_c2.queues.queue_definition import QueueDefinition


class LocalCentralApi(DefaultCentralApi):
    async def create_queue(self, queue_definition: QueueDefinition, creator_identifier: str | None = None, fail_if_exists: bool = True):
        queue = super().create_queue(queue_definition, creator_identifier, fail_if_exists)
        return await LocalQueueController(queue)
