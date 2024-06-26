from typing import Any
from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_creator import QueueCreator

from turbo_c2.queues.queue_definition import QueueDefinition


class LocalQueueCreator(QueueCreator):
    def create(self, definition: QueueDefinition, meta: dict[str, Any] | None=None) -> QueueController[Any]:
        return self.queue_type(definition.name)
