import asyncio
import itertools
import time
from typing import Iterable
from turbo_c2.domain.gui.layout_element import EdgeLayoutElement, LayoutElement
from turbo_c2.turbo_events.commands.dispatch_event_command import DispatchEventCommand
from turbo_c2.turbo_events.commands.dispatch_events_command import DispatchEventsCommand
from turbo_c2.turbo_events.commands.get_handlers_by_event_type_command import (
    GetHandlersByEventTypeCommand,
)
from turbo_c2.turbo_events.commands.get_handler_layout_elements_command import (
    GetHandlerLayoutElementsCommand,
)
from turbo_c2.turbo_events.commands.handler_store_controller_definition import HandlerStoreControllerDefinition
from turbo_c2.turbo_events.commands.handler_store_creator_definition import HandlerStoreCreatorDefinition
from turbo_c2.turbo_events.commands.handler_store_crud import HandlerStoreCrud
from turbo_c2.turbo_events.commands.handler_store_type_definition import HandlerStoreTypeDefinition
from turbo_c2.turbo_events.commands.register_handlers_command import RegisterHandlersCommand
from turbo_c2.turbo_events.event_store.handler_store import HandlerStore
from turbo_c2.turbo_events.events.event import Event
from turbo_c2.turbo_events.handlers.local_handler_controller import LocalHandlerController
from turbo_c2.extra_api.command.group.get_job_group_with_instances_command import (
    GetJobGroupWithInstancesCommand,
)
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.extra_api.command.job.job_instance_crud import JobInstanceCrud
from turbo_c2.extra_api.command.queue.create_queue_command import CreateQueueCommand
from turbo_c2.turbo_events.commands.event_store_controller_definition import (
    EventStoreControllerDefinition,
)
from turbo_c2.turbo_events.commands.event_store_creator_definition import (
    EventStoreCreatorDefinition,
)
from turbo_c2.turbo_events.commands.event_store_crud import EventStoreCrud
from turbo_c2.turbo_events.commands.event_store_type_definition import (
    EventStoreTypeDefinition,
)
from turbo_c2.turbo_events.commands.register_handler_command import (
    RegisterHandlerCommand,
)
from turbo_c2.extra_api.command.queue.get_queues_by_type_command import GetQueuesByTypeCommand
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.jobs.edge_representation import EdgeRepresentation
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.jobs.target_representation import TargetRepresentation
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.interfaces.queue_api import QueueApi


class EventBasedBooleanSchedulerApi(DefaultExtraApiWithSubApis):
    def __init__(self) -> None:
        self.__apis: list[NeedsCentralApi] = [
            DefinitionResourceApi(EventStoreControllerDefinition),
            DefinitionResourceApi(EventStoreCreatorDefinition),
            DefinitionResourceApi(EventStoreTypeDefinition),
            CrudResourceApi(
                EventStoreCrud,
                creators_keys=EventStoreCreatorDefinition.get_api_reference().complete_id_path,
            ),
            DefinitionResourceApi(HandlerStoreControllerDefinition),
            DefinitionResourceApi(HandlerStoreCreatorDefinition),
            DefinitionResourceApi(HandlerStoreTypeDefinition),
            CrudResourceApi(
                HandlerStoreCrud,
                creators_keys=HandlerStoreCreatorDefinition.get_api_reference().complete_id_path,
            ),
        ]

        super().__init__(
            self.__apis,
            [
                (RegisterHandlerCommand, self.register_handler),
                (GetHandlersByEventTypeCommand, self.get_handlers_by_event_type),
                (GetHandlerLayoutElementsCommand, self.get_handler_layout_elements),
                (DispatchEventCommand, self.dispatch_event),
                (DispatchEventsCommand, self.dispatch_events),
                (RegisterHandlersCommand, self.register_handlers),
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            "event_based_boolean_scheduler",
        )

        self.queues_cache: dict[str, QueueApi] = {}
        self.handler_store_cache: dict[str, HandlerStore] = {}

    async def register_handler(self, command: RegisterHandlerCommand):
        queues = {}
        if command.controller_id:
            controller = await self.central_api.execute(
                HandlerStoreCrud.get(command.controller_id)
            )

        else:
            controller = (await self.central_api.execute(HandlerStoreCrud.get()))[0]

        for defined_queue in command.handler_controller.handler.not_evaluated_queues:
            queue: QueueApi = await self.central_api.execute(
                CreateQueueCommand(QueueDefinition(defined_queue), fail_if_exists=False)
            )
            queues[defined_queue] = queue

        await command.handler_controller.evaluate_queues(queues)
        return await controller.register_handler(command.handler_controller)
    
    async def register_handlers(self, command: RegisterHandlersCommand):
        # before_all = time.perf_counter()
        if command.controller_id:
            if command.controller_id not in self.handler_store_cache:
                self.handler_store_cache[command.controller_id] = await self.central_api.execute(
                    HandlerStoreCrud.get(command.controller_id)
                )

            controller = self.handler_store_cache[command.controller_id]

        else:
            if "default" not in self.handler_store_cache:
                self.handler_store_cache["default"] = (await self.central_api.execute(HandlerStoreCrud.get()))[0]
            
            controller = self.handler_store_cache["default"]

        handler_with_queues = []

        # before_queues = time.perf_counter()
        for handler_controller in command.handler_controllers:
            for defined_queue in handler_controller.handler.not_evaluated_queues:
                if defined_queue not in self.queues_cache:
                    queue: QueueApi = await self.central_api.execute(
                        CreateQueueCommand(QueueDefinition(defined_queue), fail_if_exists=False)
                    )
                    self.queues_cache[defined_queue] = queue
                else:
                    queue = self.queues_cache[defined_queue]

                handler_with_queues.append((handler_controller, {defined_queue: queue}))

        # print(f"Creating queues took {time.perf_counter() - before_queues} seconds")

        # before_eval = time.perf_counter()
        await asyncio.gather(*[
            handler_controller.evaluate_queues(queues)
            for handler_controller, queues in handler_with_queues
        ])

        # print(f"Evaluating queues took {time.perf_counter() - before_eval} seconds")

        # before_register = time.perf_counter()
        result = await controller.register_handlers(command.handler_controllers)
        # print(f"Registering handlers took {time.perf_counter() - before_register} seconds")

        # print(f"Registering handlers function total took {time.perf_counter() - before_all} seconds")
        return result
    
    async def dispatch_event(self, command: DispatchEventCommand):
        queues = await self.central_api.execute(
            GetQueuesByTypeCommand(Event)
        )

        await asyncio.gather(
            *[
                queue.put(command.event)
                for queue in queues
            ]
        )

    async def dispatch_events(self, command: DispatchEventsCommand):
        queues = await self.central_api.execute(
            GetQueuesByTypeCommand(Event)
        )

        await asyncio.gather(
            *[
                queue.put_iter(command.events)
                for queue in queues
            ]
        )

    async def get_handlers_by_event_type(self, command: GetHandlersByEventTypeCommand):
        if command.controller_id:
            controller: HandlerStore = await self.central_api.execute(
                HandlerStoreCrud.get(command.controller_id)
            )

        else:
            controller: HandlerStore = (
                await self.central_api.execute(HandlerStoreCrud.get())
            )[0]

        return await controller.get_handler_by_event_type(command.event_type)

    async def get_handler_layout_elements(
        self, command: GetHandlerLayoutElementsCommand
    ):
        group = await self.central_api.execute(
            GetJobGroupWithInstancesCommand(group_path=command.group_path)
        )

        if not group:
            raise RuntimeError(f"Group {command.group_path} not found")

        elements = []

        consumer_definition = (await self.central_api.execute(
            JobDefinitionCrud.get(prefix="name/consumer")
        ))[0]

        consumer_instances: list[JobInstance] = await self.central_api.execute(
            JobInstanceCrud.get(
                prefix=f"job_definition_id/{consumer_definition.resource_id}"
            )
        )

        consumer_instances_ids = []

        for consumer_instance in consumer_instances:
            consumer_instances_ids.append(
                EdgeLayoutElement(
                    representation=EdgeRepresentation.EXECUTION,
                    target=consumer_instance.resource_id,
                    target_representation=TargetRepresentation.INSTANCE,
                )
            )

        for instance in group.job_instances:
            if instance.job_definition.meta.get("dispatches"):
                handlers: Iterable[LocalHandlerController] = itertools.chain(
                    await self.central_api.execute(
                        *[
                            GetHandlersByEventTypeCommand(event_type=dispatch.get_type())
                            for dispatch in instance.job_definition.meta["dispatches"]
                        ]
                    )
                )
                for handler in handlers:

                    edge_true_elements = []
                    edge_false_elements = []

                    true_output_queues = (await handler.get_when_true()).output_queues
                    for output_queue_reference in true_output_queues:
                        handler_true_instances: list[JobInstance] = await self.central_api.execute(
                            JobInstanceCrud.get(
                                prefix=f"input_queue_reference/{output_queue_reference}"
                            )
                        )

                        edge_true_elements.extend(
                            [
                                EdgeLayoutElement(
                                    representation=EdgeRepresentation.CONDITION_TRUE,
                                    target=target.resource_id,
                                    target_representation=TargetRepresentation.INSTANCE,
                                )
                                for target in handler_true_instances
                            ]
                        )

                    false_output_queues = (await handler.get_when_false()).output_queues
                    for output_queue_reference in false_output_queues:
                        handler_false_instances: list[JobInstance] = await self.central_api.execute(
                            JobInstanceCrud.get(
                                prefix=f"input_queue_reference/${output_queue_reference}"
                            )
                        )

                        edge_false_elements.extend(
                            [
                                EdgeLayoutElement(
                                    representation=EdgeRepresentation.CONDITION_FALSE,
                                    target=target.resource_id,
                                    target_representation=TargetRepresentation.INSTANCE,
                                )
                                for target in handler_false_instances
                            ]
                        )

                    elements.append(
                        LayoutElement(
                            representation=NodeRepresentation.DECISION,
                            resource_name=await (handler.get_name()),
                            sources=consumer_instances_ids,
                            destinations=[*edge_true_elements, *edge_false_elements],
                        )
                    )
    
        return elements
