from typing import Any
from turbo_c2.queues.queue_reference import QueueReference
from turbo_c2.interfaces.queue_api import QueueApi


class NeedsQueueEvaluation:
    def __init__(
        self,
        queues_reference: list[QueueReference] | None = None,
        queues_reference_mapping: dict[QueueReference, QueueApi] | None = None,
    ):
        if not isinstance(queues_reference_mapping, dict) and not queues_reference_mapping is None:
            raise TypeError(f"queues_reference_mapping must be a dict or None, not {type(queues_reference_mapping)}")

        self.__cache = (
            queues_reference_mapping
            if queues_reference_mapping
            else {x: None for x in (queues_reference or [])}
        )
        self.__evaluated = self.is_all_evaluated(queues_reference, self.__cache)
        self.__evaluated_queue_mapping: dict[QueueReference, QueueApi] = {}

    @property
    def evaluated_queues(self):
        return list(
            filter(lambda x: self.__cache.get(x) is not None, self.__cache.keys())
        )

    @property
    def not_evaluated_queues(self):
        return list(filter(lambda x: self.__cache.get(x) is None, self.__cache.keys()))

    @property
    def queue_identificators(self):
        return list(self.__cache.keys())

    @property
    def queue_mapping(self):
        return self.__cache

    @property
    def evaluated_queue_mapping(self):
        if not self.evaluated:
            raise Exception("Queues not evaluated yet")

        if not self.__evaluated_queue_mapping:
            queue_mapping: dict[QueueReference, QueueApi] = {}
            for queue_reference, queue_api in self.__cache.items():
                if queue_api:
                    queue_mapping[queue_reference] = queue_api
                else:
                    raise Exception(f"Queue {queue_reference} not evaluated")

            self.__evaluated_queue_mapping = queue_mapping

        return self.__evaluated_queue_mapping

    @property
    def evaluated(self):
        return self.__evaluated

    def add_queue(
        self, queue_reference: QueueReference, queue_api: QueueApi | None = None
    ):
        self.__cache[queue_reference] = queue_api
        if not queue_api and self.__evaluated:
            self.__evaluated = False
        elif self.__evaluated_queue_mapping:
            self.__evaluated_queue_mapping[queue_reference] = queue_api

    def remove_queue(
        self,
        queue_reference: QueueReference,
        fail_if_not_found: bool = True,
        default: Any = None,
    ):
        if fail_if_not_found and queue_reference not in self.__cache:
            raise KeyError(f"Queue {queue_reference} not found")

        return self.__cache.pop(queue_reference, default)

    def is_all_evaluated(
        self,
        queues_reference: list[QueueReference] | None = None,
        queues_reference_mapping: dict[QueueReference, QueueApi] | None = None,
    ):
        has_all_elements = all(
            [
                queues_reference_mapping.get(queue_reference)
                for queue_reference in (queues_reference or [])
            ]
        )
        has_same_length = len((queues_reference or [])) == len(queues_reference_mapping)

        return has_all_elements and has_same_length

    async def evaluate_queues(self, queue_mapping: dict[QueueReference, QueueApi]):
        if self.__evaluated:
            raise Exception("Queues already evaluated.")

        self.__cache.update(
            {queue: queue_mapping[queue] for queue in self.not_evaluated_queues}
        )
        self.__evaluated = self.is_all_evaluated(
            self.queue_identificators, self.__cache
        )

        self.after_evaluation()

        return None

    def after_evaluation(self):
        pass

    def __reduce__(self):
        return (NeedsQueueEvaluation, (self.not_evaluated_queues, self.__cache))
