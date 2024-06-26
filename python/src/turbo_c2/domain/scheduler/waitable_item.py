from dataclasses import dataclass
from typing import Any, Callable, Coroutine


@dataclass
class WaitableItem():
    wait_function: Callable[[], Coroutine[Any, Any, None]]
    graceful_shutdown_function: Callable[[], Coroutine[Any, Any, None]]
    name: str
