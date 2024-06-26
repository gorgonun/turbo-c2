from __future__ import annotations
from turbo_c2.turbo_events.events.event_reference import EventReference


class HasReference:
    def __init__(self, reference: EventReference) -> None:
        self.__reference = reference

    @property
    def reference(self):
        return self.__reference
    

class HasReferences:
    def __init__(self, references: list[EventReference]) -> None:
        self.__references = references

    @property
    def references(self):
        return self.__references
