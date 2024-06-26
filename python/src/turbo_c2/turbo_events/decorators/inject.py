import functools
import inspect
from typing import Any, Callable, TypeVar

from ebf.ebf_global import scheduler_globals


T = TypeVar("T")


def injectable(name: str | None = None):
    def wrapped(func: Callable[..., T]):
        object_name = name or func.__name__
        created_object = func()
        old_object: dict[str, dict[str, list[Any]] | dict[type[Any], list[Any]]] = scheduler_globals.get_shared_object("injectable") or {"name": {}, "annotation": {}}
        old_object["name"].setdefault(object_name, []).append(created_object)
        old_object["annotation"].setdefault(type(created_object), []).append(created_object)
        scheduler_globals.set_shared_object("injectable", old_object)
    return wrapped



def inject():
    def wrapped(func):
        injectable_kwargs: dict[str, Any] = {}
        injectable_mapping: dict[str, dict[str, list[Any]] | dict[type[Any], list[Any]]] = scheduler_globals.get_shared_object("injectable")

        for parameter in inspect.signature(func).parameters.values():
            checking_type = Any if parameter.annotation is inspect.Parameter.empty else parameter.annotation
            injectable_name_mapping = injectable_mapping["name"].get(parameter.name, [])
            injectable_type_mapping = injectable_mapping["annotation"].get(parameter.annotation, [])

            if not injectable_name_mapping and not injectable_type_mapping:
                raise Exception(f"No injectable object found for {parameter.name} with type {checking_type}.")
            
            elif len(injectable_name_mapping) == 1 and (not injectable_type_mapping or (len(injectable_type_mapping) == 1 and injectable_name_mapping[0] == injectable_type_mapping[0])):
                injectable_kwargs[parameter.name] = injectable_name_mapping[0]

            elif len(injectable_type_mapping) == 1 and (not injectable_name_mapping or (len(injectable_name_mapping) == 1 and injectable_name_mapping[0] == injectable_type_mapping[0])):
                injectable_kwargs[parameter.name] = injectable_type_mapping[0]

            else:
                raise Exception(f"Multiple injectable objects found for {parameter.name} with type {checking_type}.")
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **injectable_kwargs, **kwargs)

        return wrapper
    return wrapped
