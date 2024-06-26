import abc
from turbo_c2.turbo_events.events.event_reference import EventReference


class EventController(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def event_happened(self, event_reference: EventReference) -> bool:
        pass

    
