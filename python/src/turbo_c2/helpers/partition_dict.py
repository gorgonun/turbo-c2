import abc
from dataclasses import dataclass
import dataclasses
from typing import Any, Callable, ClassVar, Dict, Generic, Hashable, Protocol, TypeVar


# class IsDataclass(Protocol):
#     __dataclass_fields__: ClassVar[Dict] 


# U = TypeVar("U", bound=IsDataclass)

class GenericReference():
    def __repr__(self) -> str:
        return "GenericReference(*)"
    
    def __eq__(self, o: object) -> bool:
        return hash(o) == hash(self)
    
    def __hash__(self) -> int:
        return hash("GenericReference(*)")


V = TypeVar("V")

@dataclass
class Identifier(Generic[V]):
    pass


@dataclass
class EBFSchema(abc.ABC):
    @property
    def identifiers(self) -> list[Hashable]:
        pass

    @property
    def composed_identifiers(self) -> list[Hashable]:
        pass


@dataclass
class DefaultSchema(EBFSchema):
    identifiers: list[Hashable] = []

    def __post_init__(self):
        for field in dataclasses.fields(self):
            if field.type == Identifier:
                self.identifiers.append(field.name)

    @property
    def composed_identifiers(self) -> list[Hashable]:
        return list(dataclasses.asdict(self).keys()) if not self.identifiers else []


# def schema():
#     def wrapper(cls: U):
#         return cls
#     return wrapper


@dataclass
class Neo4JNodeCreatedEventSchema(DefaultSchema):
    node_id: Identifier[int]
    processing_id: Identifier[str]
    node: Node

    @property
    def composed_identifiers(self) -> list[Hashable]:
        return [self.node_id, self.processing_id]


T = TypeVar("T", bound=EBFSchema)


class PartitionManager(Generic[T], abc.ABC):
    
    def get_data_by_partition_order(self, identifiable: T) -> list[tuple[Hashable, Any]]:
        pass

    @classmethod
    def get_partition_order(cls) -> list[Hashable]:
        pass


class DefaultPartitionManager(PartitionManager[T]):
    def get_data_by_partition_order(self, identifiable: T) -> list[tuple[Hashable, Any]]:
        identifiable_fields = identifiable.identifiers or identifiable.composed_identifiers
        if not identifiable_fields:
            raise Exception("No identifiable fields found in", identifiable)

        return [(field, getattr(identifiable, field)) for field in identifiable_fields]

class PartitionedDict():
    def __init__(self) -> None:
        self.__dict = dict()

    def insert(self, ordered_data_by_partition: list[tuple[Hashable, Any]], value: Any) -> None:
        cursor = self.__dict
        last_partition = None

        for key, partition in ordered_data_by_partition:
            if not last_partition:
                new_partition = {partition: value}
                cursor.setdefault(key, {partition: value, GenericReference(): value})
            else:
                new_partition = {}
                if not isinstance(cursor[last_partition], dict):
                    cursor[last_partition] = new_partition

                if not isinstance(cursor[GenericReference()], dict):
                    cursor[GenericReference()] = new_partition

                cursor[last_partition].update({partition: value, GenericReference(): value})
            last_partition = partition

        if isinstance(value, dict):
            cursor = self.__dict.get(key)
            self.__dict[key] = value
