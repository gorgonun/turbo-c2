from dataclasses import dataclass, field
from typing import Generic, Hashable, Type, TypeVar

from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_definition import QueueDefinition


T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=str | Type | QueueController | QueueDefinition | None)


@dataclass(frozen=True)
class QueueReference(Generic[T, U]):
    identifier: T = field(hash=True)
    reference: U | None = field(default=None, hash=False)

    def is_controller(self) -> bool:
        return isinstance(self.reference, QueueController)
    
    def is_type(self) -> bool:
        return isinstance(self.reference, type)
    
    def is_str(self) -> bool:
        return isinstance(self.reference, str)
    
    def __str__(self) -> str:
        return str(self.identifier)
    
    def __hash__(self) -> int:
        return hash(self.identifier)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QueueReference):
            return self.identifier == other
        return self.identifier == other.identifier
