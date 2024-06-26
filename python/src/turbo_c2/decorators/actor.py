from dataclasses import dataclass, field
import inspect
import os
from typing import Any, Callable, Coroutine, Generic, Hashable, Type, TypeVar

import ray

from turbo_c2.extra_api.command.crud_client_resource_command import CrudClientResourceCommand
from turbo_c2.extra_api.command.crud_command import CrudCommand
from turbo_c2.extra_api.command.definition_command import DefinitionCommand
from turbo_c2.extra_api.crud_client_resource_api import CrudClientResourceApi
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.globals.ebf_global import get_scheduler_globals
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.resource_creator import ResourceCreator
from turbo_c2.jobs.needs_central_api import NeedsCentralApi


ACTOR = TypeVar("ACTOR")
API = TypeVar("API")


@dataclass
class ActorDefinition(Generic[ACTOR]):
    actor_class: Type[ACTOR]
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class RemoteGenericCreator(ResourceCreator[ActorDefinition], NeedsCentralApi):
    async def create(
        self,
        definition: ActorDefinition,
        meta: dict[str, Any] | None = None,
    ):
        kwargs = {}

        params = inspect.signature(definition.actor_class).parameters

        # FIXME: Merge dict deeply nested
        if params.get("meta"):
            kwargs["meta"] = {**meta, **(definition.meta or {})}

        if params.get("central_api"):
            kwargs["central_api"] = self.central_api

        actor_ref = ray.remote(definition.actor_class).remote(
            *(definition.args or []),
            **(definition.kwargs or {}),
            **kwargs
        )

        return actor_ref


@dataclass
class ActorResult(Generic[ACTOR]):
    actor_ref: ACTOR | None
    creator_definition: DefinitionCommand[str, RemoteGenericCreator]
    api_definition: DefinitionCommand[Hashable, API] | None
    resource_manager: (
        CrudCommand[ActorDefinition, ACTOR]
        | CrudClientResourceCommand[ActorDefinition, ACTOR, API]
    )


def actor(
    name: str,
    api_identifier: str | None = None,
    api_path: str | None = None,
    api: API | None = None,
    create_resource: bool = True
):
    def wrapper(func: Callable[[CentralApi], Coroutine[Any, Any, ActorDefinition[ACTOR]]]):
        actor_api_identifier = api_identifier or "generic_actor_api"
        actor_api_path = os.path.join(api_path or '', name)
        
        async def on_receive_params(central_api: CentralApi):
            kwargs = {}
            if inspect.signature(func).parameters.get("central_api"):
                kwargs["central_api"] = central_api

            if inspect.iscoroutinefunction(func):
                definition = await func(**kwargs)

            else:
                definition = func(**kwargs)

            class GenericCreatorDefinition(
                DefinitionCommand[str, RemoteGenericCreator]
            ):
                api_identifier = actor_api_identifier
                api_path = os.path.join(actor_api_path, "creators/creator")

            class GenericApiDefinition(DefinitionCommand[Hashable, API]):
                api_identifier = actor_api_identifier
                api_path = actor_api_path
                api_path = os.path.join(actor_api_path, "apis/api")

            actor_creator = RemoteGenericCreator(central_api)

            if api is not None:

                class GenericClientResource(
                    CrudClientResourceCommand[ActorDefinition, ACTOR, API]
                ):
                    api_identifier = actor_api_identifier
                    api_path = os.path.join(actor_api_path, "resources/resource")

                resource_manager_definition = GenericClientResource

            else:

                class GenericResource(CrudCommand[ActorDefinition, ACTOR]):
                    api_identifier = actor_api_identifier
                    api_path = actor_api_path

                resource_manager_definition = GenericResource

            class GenericExtraApi(DefaultExtraApiWithSubApis):
                def __init__(self) -> None:
                    self.__apis = [
                        DefinitionResourceApi(GenericCreatorDefinition),
                        DefinitionResourceApi(GenericApiDefinition),
                    ]

                    if api is not None:
                        self.__apis.append(
                            CrudClientResourceApi(
                                resource_manager_definition,
                                creators_keys=GenericCreatorDefinition.get_api_reference().complete_id_path,
                                apis_keys=GenericApiDefinition.get_api_reference().complete_id_path,
                            )
                        )

                    else:
                        self.__apis.append(
                            CrudResourceApi(
                                resource_manager_definition,
                                creators_keys=GenericCreatorDefinition.get_api_reference().complete_id_path,
                            )
                        )

                    super().__init__(
                        self.__apis,
                        [
                            *[
                                command
                                for api in self.__apis
                                for command in api.get_command_structure()
                            ],
                        ],
                        actor_api_identifier,
                    )

            extra_api = GenericExtraApi()
            extra_api.add_central_api(central_api)

            await central_api.put_extra_api(extra_api)
            await central_api.execute(
                GenericCreatorDefinition.set(resource_id="default", resource=actor_creator)
            )

            if api is not None:
                await central_api.execute(GenericApiDefinition.set(resource_id="default", resource=api))

            new_actor = None

            if create_resource:
                new_actor = await central_api.execute(
                    resource_manager_definition.create(resource_id="default", definition=definition)
                )

            result = ActorResult(
                actor_ref=new_actor,
                creator_definition=GenericCreatorDefinition,
                api_definition=GenericApiDefinition if api is not None else None,
                resource_manager=resource_manager_definition,
            )

            await central_api.put_remote_object_reference(
                ["resource_creator", "actor", actor_api_identifier, *actor_api_path.split("/")],
                result,
            )

        get_scheduler_globals().set_resource_mapping(
            ["init", "needs_central_api", actor_api_identifier, *actor_api_path.split("/")], on_receive_params
        )

        async def get_result(central_api: CentralApi) -> ActorResult[ACTOR]:
            return await central_api.get_object_reference(
                ["resource_creator", "actor", actor_api_identifier, actor_api_path]
            )

        return get_result
    return wrapper
