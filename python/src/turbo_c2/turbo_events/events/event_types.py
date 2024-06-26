from typing import Generic, TypeVar


DataType = TypeVar("DataType", str, int, float, bool)

class EventId(Generic[DataType]):
    pass
