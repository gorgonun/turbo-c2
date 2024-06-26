from typing import AsyncIterator, Generic, TypeVar, cast
from turbo_c2.helpers.name_utils import NameUtils
from turbo_c2.mixin.needs_queue_evaluation import NeedsQueueEvaluation
from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T")


class Consumer(NeedsQueueEvaluation, Generic[T]):
    def __init__(self, queue_definition: QueueDefinition[T], name: str | None = None):
        self.__name = name or NameUtils.get_anonymous_name(self.anonymous_preffix())
        self.__queue_definition = queue_definition
        self.__queue = None
        super().__init__(queues_reference=[queue_definition.name])

    @property
    def name(self):
        return self.__name
    
    @property
    def queue(self):
        if not self.__queue:
            self.__queue = cast(QueueController[T], self.evaluated_queues[self.__queue_definition.name])
        return self.__queue

    async def __aiter__(self) -> AsyncIterator[T]:
        async for content in self.queue:
            yield content

    def anonymous_preffix(self):
        return "AnonymousConsumer"
