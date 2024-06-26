import abc
from typing import Any, Generic

from turbo_c2.helpers.generics import DEFINITION


class ResourceCreator(Generic[DEFINITION], abc.ABC):
    @abc.abstractmethod
    async def create(self, definition: DEFINITION, meta: dict[str, Any]):
        pass
