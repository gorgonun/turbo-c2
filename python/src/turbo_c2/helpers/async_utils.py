from asyncio import as_completed
import functools
from typing import Any, Awaitable, Callable, Coroutine, Iterable

from turbo_c2.helpers.generics import DATA, INPUT, OUTPUT


def async_lambda(f: Callable[INPUT, OUTPUT]) -> Callable[INPUT, Awaitable[OUTPUT]]:
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def coroutine(data: DATA):
    async def wrapper() -> DATA:
        return data

    return wrapper()


async def amap(f: Callable[INPUT, Coroutine[Any, Any, OUTPUT]], datum: Iterable[Coroutine[Any, Any, DATA]]):
    for data in as_completed(datum):
        yield f(await data)
