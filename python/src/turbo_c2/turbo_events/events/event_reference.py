from typing import Any, Hashable


class EventReference():
    def __init__(self, event_type: str, by_identificators: bool, values: list[tuple[str, Any]] | None=None, identificator_data: list[tuple[Hashable, Any]]=None) -> None:
        self.__event_type = event_type
        self.__values = values or []
        self.__by_identificators = by_identificators
        self.__generic = len(self.__values) == 0
        self.__identificator_data = identificator_data or []
        
        if by_identificators and not self.__identificator_data:
            raise Exception("Values must be provided when content can be identificated.")

    @property
    def reference(self):
        """
        When by_identificators is True there is no identification and when it is False there are no properties.
        """
        return "/".join([self.event_type, self.properties_reference])
    
    @property
    def properties_reference(self):
        return "/".join([str(x) for kv in self.get_properties_data() for x in kv])
    
    @property
    def event_type(self):
        return self.__event_type
    
    @property
    def identification(self) -> str | None:
        if self.by_identificators:
            data = self.get_identification_data()

            if not data:
                raise RuntimeError("True by_identificators, but no identificators found.")

            return "/".join([x for x in data])
        return None
    
    @property
    def properties(self) -> str | None:
        if not self.by_identificators:
            return None
        return "/".join(["/".join([name, value]) for (name, value) in self.get_properties_data()])
    
    @property
    def by_identificators(self):
        return self.__by_identificators
    
    @property
    def generic(self):
        return self.__generic
    
    def get_identification_data(self) -> list[tuple[str, Any]] | None:
        if self.by_identificators:
            return self.__identificator_data
        return None
    
    def get_properties_data(self) -> list[tuple[str, Any]]:
        if self.by_identificators:
            data = self.get_identification_data()
            if not data:
                raise RuntimeError("True by_identificators, but no identificators found.")
            return data
        return self.__values
    
    def tuples(self):
        return self.get_properties_data()
    
    def __str__(self) -> str:
        return self.properties_reference
    
    def __repr__(self) -> str:
        return self.reference
    
    def __hash__(self) -> int:
        return hash(self.reference)
    
    def __eq__(self, other) -> bool:
        return self.reference == getattr(other, "reference", None)
