from dataclasses import asdict, dataclass, field, fields
import datetime
import functools
import typing
from turbo_c2.turbo_events.events.empty_element import EmptyElement
from turbo_c2.turbo_events.events.event_types import EventId
from turbo_c2.helpers.date_time import DateTime
from turbo_c2.turbo_events.events.event_reference import EventReference


@dataclass(kw_only=True, frozen=True)
class Event:
    happened_at: datetime.datetime = field(default_factory=DateTime.now)

    @property
    def reference(self) -> EventReference:
        if self.has_id():
            return self.get_reference(**self.get_id_data())
        return self.get_reference(**self.data())

    def get_id_fields(self):
        if self.has_id():
            return [
                f.name for f in fields(self) if typing.get_origin(f.type) == EventId
            ]
        return [f.name for f in fields(self)]

    def data(self):
        return asdict(self)

    def get_id_data(self):
        return {index: getattr(self, index) for index in self.get_id_fields()}

    def tuples(self):
        return sorted(
            [(x.name, getattr(self, x.name)) for x in fields(self)], key=lambda x: x[0]
        )

    def __hash__(self) -> int:
        return hash(self.reference)
    
    def __eq__(self, other) -> bool:
        return self.reference == getattr(other, "reference", None)

    def __repr__(self) -> str:
        return f"{self.__name__}({self.reference})"

    @classmethod
    def fields(cls):
        return [x.name for x in fields(cls)]

    @classmethod
    def has_id(cls):
        return any([f for f in fields(cls) if typing.get_origin(f.type) == EventId])

    @classmethod
    def get_reference(cls, **kwargs):
        allowed_fields = {f.name: f for f in fields(cls)}
        is_identificable = False
        reference_fields = []
        identification_fields = []

        for field_name, field_cls in allowed_fields.items():
            if field_name not in kwargs:
                reference_fields.append((field_name, EmptyElement))

            else:
                value = kwargs.pop(field_name)

                field_type = field_cls.type

                if typing.get_origin(field_type) == EventId and not is_identificable:
                    is_identificable = True
                    reference_fields = [(field_name, value)]
                    identification_fields = [(field_name, value)]

                else:
                    reference_fields.append((field_name, value))

        if len(kwargs) > 0:
            raise RuntimeError(f"Unexpected kwargs {kwargs} for {cls}")

        return EventReference(
            event_type=cls.__name__,
            values=sorted(reference_fields, key=lambda x: x[0]),
            by_identificators=is_identificable,
            identificator_data=identification_fields
        )

    @classmethod
    def ref(cls, **kwargs):
        return cls.get_reference(**kwargs)

    @classmethod
    def get_type(cls):
        return cls.__name__
    
    def __reduce__(self) -> str | tuple[typing.Any, ...]:
        return functools.partial(self.__class__, **self.data()), ()
