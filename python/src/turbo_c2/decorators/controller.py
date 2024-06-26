import abc
from typing import Callable, Type, TypeVar

from fastapi import FastAPI

from turbo_c2.globals.ebf_global import get_scheduler_globals_object
from ray import serve

from turbo_c2.interfaces.central_api import CentralApi


class Controller(abc.ABC):
    @abc.abstractmethod
    def bind(self):
        pass


CONTROLLER = TypeVar("CONTROLLER", bound=Controller)
DEPLOYMENT = TypeVar("DEPLOYMENT")


def controller(name: str, *args, **kwargs):
    def wrapper(func: Callable[[FastAPI, CentralApi], Type[DEPLOYMENT]]):
        def with_data(app: FastAPI, central_api: CentralApi):
            controller_class = func(app, central_api)
            controller_deployment = serve.deployment()(
                serve.ingress(app)(controller_class)
            )
            return controller_deployment, args, kwargs, name

        get_scheduler_globals_object().set_resource_mapping(
            ["init", "deployment_constructor", name], with_data
        )

    return wrapper
