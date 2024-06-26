from typing import Any, Callable, Coroutine
import uuid

from turbo_c2.globals.ebf_global import get_scheduler_globals
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.external_api import ExternalApi
from turbo_c2.interfaces.extra_api import ExtraApi


def extra_api(name: str | None = None):
    def wrapper(func: Callable[[CentralApi, dict[str, ExternalApi]], tuple[ExtraApi, Callable[[CentralApi], Coroutine[Any, Any, None]]]]) -> None:
        async def with_data(central_api: CentralApi, external_apis: dict[str, ExternalApi]):
            new_extra_api, with_central_api = func(central_api, external_apis)
            await central_api.put_extra_api(new_extra_api)

            if with_central_api is not None:
                await with_central_api(central_api)

            return new_extra_api

        get_scheduler_globals().set_resource_mapping(
            ["init", "extra_api_constructor", name or uuid.uuid4().hex], with_data
        )

    return wrapper
