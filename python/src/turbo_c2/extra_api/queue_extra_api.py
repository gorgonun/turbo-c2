import asyncio
from typing import Any, Type
from turbo_c2.extra_api.command.queue.create_queue_command import CreateQueueCommand
from turbo_c2.extra_api.command.queue.get_queue_api_command import GetQueueApiCommand
from turbo_c2.extra_api.command.queue.get_queue_apis_command import GetQueueApisCommand
from turbo_c2.extra_api.command.queue.get_queue_command import GetQueueCommand
from turbo_c2.extra_api.command.queue.get_queue_configuration_command import (
    GetQueueConfigurationCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_controller_command import (
    GetQueueControllerCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_controllers_command import (
    GetQueueControllersCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_creator_command import GetQueueCreatorCommand
from turbo_c2.extra_api.command.queue.get_queue_creators_command import (
    GetQueueCreatorsCommand,
)
from turbo_c2.extra_api.command.queue.get_queue_type_command import GetQueueTypeCommand
from turbo_c2.extra_api.command.queue.get_queue_types_command import GetQueueTypesCommand
from turbo_c2.extra_api.command.queue.get_queues_by_type_command import (
    GetQueuesByTypeCommand,
)
from turbo_c2.extra_api.command.queue.get_queues_command import GetQueuesCommand
from turbo_c2.extra_api.command.queue.set_queue_api_command import SetQueueApiCommand
from turbo_c2.extra_api.command.queue.set_queue_configuration_command import (
    SetQueueConfigurationCommand,
)
from turbo_c2.extra_api.command.queue.set_queue_controller_command import (
    SetQueueControllerCommand,
)
from turbo_c2.extra_api.command.queue.set_queue_creator_command import SetQueueCreatorCommand
from turbo_c2.extra_api.command.queue.set_queue_type_command import SetQueueTypeCommand
from turbo_c2.extra_api.command.queue.update_queue_command import UpdateQueueCommand
from turbo_c2.extra_api.default_extra_api import DefaultExtraApi
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_creator import QueueCreator
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces import queue_api


class QueueExtraApi(DefaultExtraApi):
    def __init__(self) -> None:
        super().__init__(
            [
                (CreateQueueCommand, self.create_queue),
                (UpdateQueueCommand, self.update_queue),
                (GetQueueCommand, self.get_queue),
                (GetQueuesCommand, self.get_queues),
                (SetQueueCreatorCommand, self.set_queue_creator),
                (GetQueueCreatorCommand, self.get_queue_creator),
                (GetQueueCreatorsCommand, self.get_queue_creators),
                (GetQueuesByTypeCommand, self.get_queues_by_type),
                (SetQueueConfigurationCommand, self.set_configuration),
                (GetQueueConfigurationCommand, self.get_configuration),
                (GetQueueControllerCommand, self.get_queue_controller),
                (SetQueueControllerCommand, self.set_queue_controller),
                (GetQueueControllersCommand, self.get_queue_controllers),
                (GetQueueApiCommand, self.get_queue_api),
                (SetQueueApiCommand, self.set_queue_api),
                (GetQueueApisCommand, self.get_queue_apis),
                (GetQueueTypeCommand, self.get_queue_type),
                (SetQueueTypeCommand, self.set_queue_type),
                (GetQueueTypesCommand, self.get_queue_types),
            ],
            "turbo",
        )

        self.__queue_creators_path = "queue_creators"
        self.__queue_controller_path = "queue_controller"
        self.__queue_api_path = "queue_api"
        self.__queue_type_path = "queue_type"
        self.__queues_path = "queues"
        self.__api_identifier = "turbo"
        self.__configurations_path = "configurations"

    @property
    def queue_creators_complete_path(self):
        return [self.__api_identifier, self.__queue_creators_path]

    @property
    def queues_complete_path(self):
        return [self.__api_identifier, self.__queues_path]

    @property
    def configurations_path(self):
        return [self.__api_identifier, self.__configurations_path]

    @property
    def queue_controller_complete_path(self):
        return [self.__api_identifier, self.__queue_controller_path]

    @property
    def queue_api_complete_path(self):
        return [self.__api_identifier, self.__queue_api_path]

    @property
    def queue_type_complete_path(self):
        return [self.__api_identifier, self.__queue_type_path]

    async def __get_queue(self, name: str) -> queue_api.QueueApi | None:
        self.logger.debug("Getting queue", name)
        return await self.central_api.get_object_reference(
            [*self.queues_complete_path, name]
        )

    async def __put_queue(self, name: str, queue: QueueController) -> None:
        return await self.central_api.put_remote_object_reference(
            [*self.queues_complete_path, name], queue
        )

    async def __get_queue_creator(self, name: str) -> QueueCreator | None:
        return await self.central_api.get_object_reference(
            [*self.queue_creators_complete_path, name]
        )

    async def __put_queue_creator(self, name: str, creator: QueueCreator) -> None:
        return await self.central_api.put_remote_object_reference(
            [*self.queue_creators_complete_path, name], creator
        )

    async def __get_queue_controller(self, name: str) -> QueueController | None:
        return await self.central_api.get_object_reference(
            [*self.queue_controller_complete_path, name]
        )

    async def __put_queue_controller(
        self, name: str, controller: QueueController
    ) -> None:
        return await self.central_api.put_remote_object_reference(
            [*self.queue_controller_complete_path, name], controller
        )

    async def __get_queue_api(self, name: str) -> queue_api.QueueApi | None:
        return await self.central_api.get_object_reference(
            [*self.queue_api_complete_path, name]
        )

    async def __put_queue_api(self, name: str, api: queue_api.QueueApi) -> None:
        return await self.central_api.put_remote_object_reference(
            [*self.queue_api_complete_path, name], api
        )

    async def __get_queue_type(
        self, name: str | None = None, queue_hash: Type[QueueDefinition] | None = None
    ) -> Type[EBFQueue] | None:
        if name:
            return await self.central_api.get_object_reference(
                [*self.queue_type_complete_path, name]
            )
        elif queue_hash:
            return await self.central_api.get_object_reference(
                [*self.queue_type_complete_path, queue_hash]
            )

        raise ValueError("Either name or queue_hash must be provided")

    async def __put_queue_type(
        self, name: str, queue_type: Type[EBFQueue], queue_hash: Type[QueueDefinition]
    ) -> None:
        return await asyncio.gather(
            self.central_api.put_remote_object_reference(
                [*self.queue_type_complete_path, name], queue_type
            ),
            self.central_api.put_remote_object_reference(
                [*self.queue_type_complete_path, queue_hash], queue_type
            ),
        )

    async def __get_configuration(self, path: list[str]) -> Any | None:
        return await self.central_api.get_object_reference(
            [*self.configurations_path, *path]
        )

    async def __put_configuration(self, path: list[str], value: Any) -> None:
        return await self.central_api.put_remote_object_reference(
            [*self.configurations_path, *path], value
        )

    async def __get_queue_by_mro(
        self, obj_or_type: Type[Any] | Any
    ) -> list[queue_api.QueueApi]:
        obj_type = obj_or_type if isinstance(obj_or_type, type) else type(obj_or_type)
        identifiers = obj_type.mro()
        self.logger.debug("Getting queues by mro", identifiers)

        return list(
            filter(
                None, [await self.__get_queue(identifier) for identifier in identifiers]
            )
        )

    async def create_queue(self, command: CreateQueueCommand):
        if not isinstance(command.queue_definition, QueueDefinition):
            raise ValueError(
                f"queue_definition must be a QueueDefinition, not {type(command.queue_definition)}"
            )

        if not command.creator_identifier:
            creator = (await self.central_api.list_objects("/".join(self.queue_creators_complete_path)))[0][1]  # type: ignore
        else:
            creator = await self.__get_queue_creator(command.creator_identifier)

        exists = await self.__get_queue(command.queue_definition.name)

        if exists:
            if command.fail_if_exists:
                raise ValueError(
                    f"Queue {command.queue_definition.name} already exists"
                )
            return exists

        queue = await creator.create(command.queue_definition, meta={"created_by": self.__api_identifier})  # type: ignore
        await asyncio.gather(
            *[
                self.__put_queue(name, queue)
                for name in [
                    command.queue_definition.name,
                    *command.queue_definition.aliases,
                ]
            ]
        )

        return queue

    async def update_queue(self, command: UpdateQueueCommand):
        exists = await self.__get_queue(command.queue_name)

        if exists:
            await self.__put_queue(command.queue_name, command.queue_api)
        else:
            raise ValueError(f"Job {command.queue_name} does not exist")

    async def get_queue(self, command: GetQueueCommand):
        exists = await self.__get_queue(command.queue_name)

        if exists:
            return exists
        else:
            raise ValueError(f"Job {command.queue_name} does not exist")

    async def get_queues(self, command: GetQueuesCommand):
        return [
            x[1]
            for x in await self.central_api.list_objects(
                prefix="/".join(self.queues_complete_path)
            )
        ]

    async def set_queue_creator(self, command: SetQueueCreatorCommand):
        return await self.__put_queue_creator(
            command.queue_creator.identifier, command.queue_creator
        )

    async def get_queue_creator(self, command: GetQueueCreatorCommand):
        return await self.__get_queue_creator(command.queue_creator_name)

    async def get_queue_creators(self, _: GetQueueCreatorsCommand):
        return [
            x[1]
            for x in await self.central_api.list_objects(
                prefix="/".join(self.queue_creators_complete_path)
            )
        ]

    async def get_queues_by_type(self, command: GetQueuesByTypeCommand):
        self.logger.debug("Get queues by type command", command)

        obj_type = (
            command.obj_or_type
            if isinstance(command.obj_or_type, type)
            else type(command.obj_or_type)
        )

        self.logger.debug("Getting queues by type", obj_type)

        global_configuration_by_type = await self.__get_configuration(
            ["queue", "replicate_by_mro"]
        )

        if global_configuration_by_type is False:
            self.logger.debug("Replicate by mro is disabled globally")
            return [*((await self.__get_queue(obj_type)) or [])]

        configuration_by_specific_type = await self.__get_configuration(
            ["queue", "replicate_by_mro", obj_type]
        )

        if configuration_by_specific_type is False:
            self.logger.debug("Replicate by mro is disabled locally")
            return [*((await self.__get_queue(obj_type)) or [])]

        else:
            return await self.__get_queue_by_mro(obj_type)

    async def set_configuration(self, command: SetQueueConfigurationCommand):
        return await self.__put_configuration(
            command.configuration_path, command.configuration_value
        )

    async def get_configuration(self, command: GetQueueConfigurationCommand):
        return await self.__get_configuration(command.configuration_path)

    async def get_queue_controller(self, command: GetQueueControllerCommand):
        return await self.__get_queue_controller(command.queue_controller_id)

    async def set_queue_controller(self, command: SetQueueControllerCommand):
        return await self.__put_queue_controller(
            command.queue_controller_id, command.queue_controller
        )

    async def get_queue_controllers(self, _: GetQueueControllersCommand):
        return [
            x[1]
            for x in await self.central_api.list_objects(
                prefix="/".join(self.queue_controller_complete_path)
            )
        ]

    async def get_queue_api(self, command: GetQueueApiCommand):
        return await self.__get_queue_api(command.queue_api_id)

    async def set_queue_api(self, command: SetQueueApiCommand):
        return await self.__put_queue_api(command.queue_api_id, command.queue_api)

    async def get_queue_apis(self, _: GetQueueApisCommand):
        return [
            x[1]
            for x in await self.central_api.list_objects(
                prefix="/".join(self.queue_api_complete_path)
            )
        ]

    async def get_queue_type(self, command: GetQueueTypeCommand):
        return await self.__get_queue_type(
            command.queue_type_id, command.queue_definition_hash
        )

    async def set_queue_type(self, command: SetQueueTypeCommand):
        return await self.__put_queue_type(
            command.queue_definition_id,
            command.queue_type,
            command.queue_definition_hash,
        )

    async def get_queue_types(self, _: GetQueueTypesCommand):
        return list(
            (
                await self.central_api.get_object_reference(
                    self.queue_type_complete_path
                )
            ).values()
        )
