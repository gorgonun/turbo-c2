from typing import Any

from pydantic import BaseModel


def is_iterable(obj: Any, string_is_iterable: bool = False, pydantic_model_is_iterable: bool = False, dict_is_iterable: bool = False) -> bool:
    try:
        iter(obj)

        if isinstance(obj, str):
            return string_is_iterable
        
        if isinstance(obj, BaseModel):
            return pydantic_model_is_iterable
        
        if isinstance(obj, dict):
            return dict_is_iterable

        return True
    except TypeError:
        return False
    

def is_async_iterable(obj: Any) -> bool:
    try:
        aiter(obj)
        return True
    except TypeError:
        return False
