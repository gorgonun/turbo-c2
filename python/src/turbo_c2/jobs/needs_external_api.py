from deprecated import deprecated
from typing import Generic, TypeVar
from turbo_c2.interfaces.external_api import ExternalApi


T = TypeVar("T", bound=ExternalApi)


@deprecated(version="0.0.1", reason="Use NeedsExternalApis instead, as this is very limited")
class NeedsExternalApi(Generic[T]):
    def __init__(self, external_api: T | None = None):
        self.__external_api: T | None = external_api

    @property
    def external_api(self):
        return self.__external_api

    @property
    def external_api_type(self) -> type[T]:
        return type(self.__external_api)
    
    def get_external_api(self) -> T | None:
        return self.__external_api
    
    def add_external_api(self, external_api: T):
        self.__external_api = external_api
