import asyncio
from dataclasses import replace
import functools
import itertools
from typing import TypeVar
from turbo_c2 import external_api
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.domain.gui.layout_definition import (
    LayoutDefinition,
    LayoutGroupDefinition,
    LayoutGroupDefinitionWithLayouts,
    WindowDefinition,
)
from turbo_c2.domain.gui.layout_element import LayoutElement
from turbo_c2.domain.gui.layout_element_command import LayoutElementCommand
from turbo_c2.external_api.json_local_storage_external_api import JsonLocalStorageExternalApi
from turbo_c2.external_api.local_storage_external_api import LocalStorageExternalApi
from turbo_c2.extra_api.command.group.get_groups_by_instances_command import (
    GetGroupsByInstancesCommand,
)
from turbo_c2.extra_api.command.group.get_job_group_with_instances_command import (
    GetJobGroupWithInstancesCommand,
)
from turbo_c2.extra_api.command.group.list_subgroups_command import ListSubgroupsCommand
from turbo_c2.extra_api.command.gui.add_new_element_command import AddNewElementCommand
from turbo_c2.extra_api.command.gui.elements_definition_resource import (
    ElementsDefinitionResource,
)
from turbo_c2.extra_api.command.gui.generate_layout_definition_for_group_command import (
    GenerateLayoutDefinitionForGroupCommand,
)
from turbo_c2.extra_api.command.gui.get_layout_definition_by_group_command import (
    GetLayoutDefinitionByGroup,
)
from turbo_c2.extra_api.command.gui.get_window_definition_for_groups_command import (
    GetWindowDefinitionForGroups,
)
from turbo_c2.extra_api.command.gui.gui_enum import GuiEnum
from turbo_c2.extra_api.command.gui.layout_definition_creator_definition import (
    LayoutDefinitionCreatorDefinition,
)
from turbo_c2.extra_api.command.gui.layout_definition_crud import LayoutDefinitionCrud
from turbo_c2.extra_api.command.gui.layout_element_command_creator_definition import (
    LayoutElementCommandCreatorDefinition,
)
from turbo_c2.extra_api.command.gui.layout_element_command_crud import (
    LayoutElementCommandCrud,
)
from turbo_c2.extra_api.command.gui.layout_group_definition_crud import (
    LayoutGroupDefinitionCrud,
)
from turbo_c2.extra_api.command.gui.get_layout_group_definition_with_layouts import (
    GetLayoutGroupDefinitionWithLayouts,
)
from turbo_c2.extra_api.command.gui.move_elements_command import MoveElementsCommand
from turbo_c2.extra_api.command.job.job_instance_crud import JobInstanceCrud
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.extra_api.resource_api import ResourceApi
from turbo_c2.helpers.grid_layout import GridLayout
from turbo_c2.helpers.job_group_utils import get_job_group_nodes
from turbo_c2.helpers.layout_definition import get_layout_definition_from_grid_layout_dict
from turbo_c2.helpers.serde.layout_definition_serde import LayoutDefinitionSerDe
from turbo_c2.helpers.serde.layout_group_definition_serde import LayoutGroupDefinitionSerDe
from turbo_c2.interfaces.external_api import ExternalApi
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.needs_external_api import NeedsExternalApi
from turbo_c2.jobs.target_representation import TargetRepresentation


Definition = TypeVar("Definition", bound=LayoutDefinition)
Resource = TypeVar("Resource", bound=LayoutDefinition)


class GuiExtraApi(
    DefaultExtraApiWithSubApis, NeedsExternalApi[JsonLocalStorageExternalApi]
):
    def __init__(self, central_api: CentralApiApi | None = None, external_api: JsonLocalStorageExternalApi | None = None) -> None:
        self.layout_group_definition_api = ResourceApi(
            LayoutGroupDefinitionCrud,
            after_read=LayoutGroupDefinitionSerDe.from_dict,
            before_write=LayoutGroupDefinitionSerDe.to_dict,
        )
        self.layout_definition_api = ResourceApi(
            LayoutDefinitionCrud,
            creators_keys=LayoutDefinitionCreatorDefinition.get_api_reference().complete_id_path,
            after_read=LayoutDefinitionSerDe.from_dict,
            before_write=LayoutDefinitionSerDe.to_dict,
        )

        self.__apis: list[DefinitionResourceApi | CrudResourceApi] = [
            DefinitionResourceApi(LayoutDefinitionCreatorDefinition),
            DefinitionResourceApi(LayoutElementCommandCreatorDefinition),
            CrudResourceApi(
                LayoutElementCommandCrud,
                creators_keys=LayoutElementCommandCreatorDefinition.get_api_reference().complete_id_path,
            ),
            self.layout_group_definition_api,
            self.layout_definition_api
        ]

        super().__init__(
            self.__apis,
            [
                (GetLayoutDefinitionByGroup, self.get_layout_definition_for_group),
                (GetWindowDefinitionForGroups, self.get_window_definition_for_groups),
                (
                    GetLayoutGroupDefinitionWithLayouts,
                    self.get_layout_group_definition_with_layouts,
                ),
                (
                    GenerateLayoutDefinitionForGroupCommand,
                    self.generate_layout_definition_for_group,
                ),
                (MoveElementsCommand, self.move_elements),
                (AddNewElementCommand, self.add_new_element),
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            GuiEnum.API_ID.value,
            central_api=central_api
        )

        if external_api:
            self.add_external_api(external_api)

        self.__lock = asyncio.Lock()

    def add_external_api(self, external_api: ExternalApi):
        self.layout_group_definition_api.add_external_api(external_api)
        self.layout_definition_api.add_external_api(external_api)
        return super().add_external_api(external_api)

    async def get_layout_group_definition_with_layouts(
        self, command: GetLayoutGroupDefinitionWithLayouts
    ) -> LayoutGroupDefinitionWithLayouts | None:
        layout_group: LayoutGroupDefinition = await self.central_api.execute(
            LayoutGroupDefinitionCrud.get(resource_id=command.layout_group_id)
        )

        if not layout_group:
            return None

        layouts = {}

        for layout_id in layout_group.group_definition_ids:
            layout: LayoutDefinition = await self.central_api.execute(LayoutDefinitionCrud.get(resource_id=layout_id))

            if layout:
                layouts[layout.resource_id] = layout

        return LayoutGroupDefinitionWithLayouts(
            resource_id=layout_group.resource_id,
            group_path=layout_group.group_path,
            group_definitions=layouts,
        )

    async def get_layout_definition_for_group(
        self, command: GetLayoutDefinitionByGroup
    ) -> LayoutDefinition | None:
        if command.layout_group_id:
            layout_group: LayoutGroupDefinitionWithLayouts = await self.central_api.execute(
                GetLayoutGroupDefinitionWithLayouts(
                    layout_group_id=command.layout_group_id
                )
            )

            if not layout_group:
                return None

            if command.layout_id:
                layout: LayoutDefinition = layout_group.group_definitions.get(
                    command.layout_id
                )

            else:
                layout: LayoutDefinition = list(
                    layout_group.group_definitions.values()
                )[0]

        elif command.layout_id:
            layout: LayoutDefinition = await self.central_api.execute(
                LayoutDefinitionCrud.get(resource_id=command.layout_id)
            )

        else:
            layout_groups: list[LayoutGroupDefinition] = await self.central_api.execute(
                LayoutGroupDefinitionCrud.get(prefix=f"group_path/{command.group_path}")
            )

            if not layout_groups:
                return None

            layout_group = layout_groups[0]

            layout_group_with_layouts = await self.central_api.execute(
                GetLayoutGroupDefinitionWithLayouts(
                    layout_group_id=layout_group.resource_id
                )
            )

            layout = list(layout_group_with_layouts.group_definitions.values())[0]

        return layout

    # FIXME: Deleting local_storage/json will cause layout definition to be recreated until application is restarted
    async def get_window_definition_for_groups(
        self, command: GetWindowDefinitionForGroups
    ) -> list[WindowDefinition | None]:
        if command.layout_id:
            layout: LayoutDefinition = await self.central_api.execute(
                LayoutDefinitionCrud.get(resource_id=command.layout_id)
            )
        else:
            layouts: list[LayoutDefinition] = await self.central_api.execute(
                LayoutDefinitionCrud.get()
            )
            if not layouts:
                return None

            layout = layouts[0]

        return [layout.job_groups.get(group_id) for group_id in command.group_paths]

    async def generate_layout_definition_for_group(
        self, command: GenerateLayoutDefinitionForGroupCommand
    ):
        async with self.__lock:
            layout_group = await self.central_api.execute(GetLayoutDefinitionByGroup(group_path=command.group_path))
            if layout_group:
                return layout_group

            group = await self.central_api.execute(
                GetJobGroupWithInstancesCommand(group_path=command.group_path)
            )

            if not group:
                raise RuntimeError(f"Group {command.group_path} not found")

            layout_elements = [
                element
                for elements in await self.execute_layout_element_commands(
                    command.group_path
                )
                for element in elements
            ]
            layout_elements_instances = set(
                [
                    edge.target
                    for element in layout_elements
                    for edge in [*(element.sources or []), *(element.destinations or [])]
                    if edge.representation == TargetRepresentation.INSTANCE
                ]
            )
            external_groups = filter(
                lambda group: group.path != command.group_path,
                await self.central_api.execute(
                    GetGroupsByInstancesCommand(list(layout_elements_instances))
                ),
            )

            groups_edge_mapping = {
                instance: group
                for instance in layout_elements_instances
                for group in external_groups
                if instance in group.job_instances
            }

            groups_edge_mapping.update(
                {instance.resource_id: group for instance in group.job_instances}
            )

            subgroups = await self.central_api.execute(
                ListSubgroupsCommand(command.group_path)
            )
            subgroups_with_instances = await asyncio.gather(
                *[
                    self.central_api.execute(
                        GetJobGroupWithInstancesCommand(group_path=sg.path)
                    )
                    for sg in subgroups
                ]
            )

            main_nodes = await get_job_group_nodes(group)
            external_input_instances = [
                (
                    external_input_queue,
                    await self.central_api.execute(
                        JobInstanceCrud.get(f"input_queue_reference/{external_input_queue}")
                    ),
                )
                for node in main_nodes
                for external_input_queue in node.external_input_queues
            ]
            external_output_instances = [
                (
                    external_output_queue,
                    await self.central_api.execute(
                        JobInstanceCrud.get(
                            f"output_queue_reference/{external_output_queue}"
                        )
                    ),
                )
                for node in main_nodes
                for external_output_queue in node.external_output_queues
            ]

            external_groups_from_main_nodes = itertools.chain.from_iterable(
                [
                    await self.central_api.execute(
                        GetGroupsByInstancesCommand(
                            list(
                                set(
                                    [
                                        external_input_instance[1].resource_id
                                        for external_input_instance in [
                                            *external_input_instances,
                                            *external_output_instances,
                                        ]
                                    ]
                                )
                            )
                        )
                    )
                ]
            )

            queue_group_instance_mapping: dict[str, list[tuple[JobGroup, JobInstance]]] = {}

            for queue, instance in [
                *external_input_instances,
                *external_output_instances,
            ]:
                for group in external_groups_from_main_nodes:
                    if instance.resource_id in group.job_instances:
                        queue_group_instance_mapping.setdefault(queue, []).append(
                            group, instance
                        )
                        break

            queue_group_instance_mapping = {
                queue: (group, instance)
                for (queue, instance) in [
                    *external_input_instances,
                    *external_output_instances,
                ]
            }

            subgroups_nodes = [
                (subgroup, await get_job_group_nodes(subgroup))
                for subgroup in subgroups_with_instances
            ]
            layout = await self.central_api.execute(
                GetLayoutDefinitionByGroup(group_path=group.path)
            )

            grid_layout = GridLayout(group.name, group.description)
            await grid_layout.load_graph(
                group,
                main_nodes,
                subgroups_nodes,
                groups_edge_mapping,
                queue_group_instance_mapping,
                layout_elements,
                layout,
            )

            if layout:
                layout_definition = layout

            else:
                self.logger.info("Creating layout definition")
                layout_definition = get_layout_definition_from_grid_layout_dict(
                    grid_layout.as_dict(), group
                )

                await self.central_api.execute(LayoutDefinitionCrud.create(definition=layout_definition, resource_id=layout_definition.resource_id))

            layout_group_definition: LayoutGroupDefinition = await self.central_api.execute(
                LayoutGroupDefinitionCrud.get(resource_id=group.resource_id)
            )

            if not layout_group_definition:
                layout_group_definition = LayoutGroupDefinition(
                    resource_id=group.resource_id,
                    group_path=group.path,
                    group_definition_ids=[layout_definition.resource_id],
                )

                await self.central_api.execute(
                    LayoutGroupDefinitionCrud.create(
                        layout_group_definition, layout_group_definition.resource_id
                    )
                )

            else:
                layout_group_definition.group_definition_ids.append(
                    layout_definition.resource_id
                )

                await self.central_api.execute(
                    LayoutGroupDefinitionCrud.update(
                        layout_group_definition, layout_group_definition.resource_id
                    )
                )

            return layout_definition

    async def execute_layout_element_command(
        self, resource_id: str, group_path: str, *args, **kwargs
    ) -> LayoutElement:
        command: LayoutElementCommand = await self.central_api.execute(
            LayoutElementCommandCrud.get(resource_id=resource_id)
        )

        return await self.central_api.execute(
            command.lazy_command(
                command.args,
                *args,
                **{"group_path": group_path, **command.kwargs, **kwargs},
            )
        )

    async def execute_layout_element_commands(
        self, group_path: str, *args, **kwargs
    ) -> list[list[LayoutElement]]:
        commands: list[LayoutElementCommand] = await self.central_api.execute(
            LayoutElementCommandCrud.get()
        )

        return await asyncio.gather(
            *[
                self.central_api.execute(
                    command.lazy_command(
                        *command.args,
                        *args,
                        **{"group_path": group_path, **command.kwargs, **kwargs},
                    )
                )
                for command in commands
            ]
        )
    
    async def add_new_element(self, command: AddNewElementCommand):
        layout: LayoutDefinition = await self.central_api.execute(
            LayoutDefinitionCrud.get(resource_id=command.layout_id)
        )

        if not layout:
            raise ValueError(f"Layout {command.layout_id} not found")

        if command.element_type == "job_instances":
            target = layout.window_definition.job_instances
        elif command.element_type == "queues":
            target = layout.window_definition.queues
        elif command.element_type == "sub_groups":
            target = layout.window_definition.sub_groups
        elif command.element_type == "items":
            target = layout.window_definition.items
        elif command.element_type == "external_groups":
            target = layout.window_definition.external_groups

        target[command.element_id] = command.element

        return await self.central_api.execute(LayoutDefinitionCrud.update(layout, layout.resource_id))

    async def move_elements(self, command: MoveElementsCommand):
        layout: LayoutDefinition = await self.central_api.execute(
            LayoutDefinitionCrud.get(resource_id=command.layout_id)
        )

        if not layout:
            raise ValueError(f"Layout {command.layout_id} not found")

        for element_id, req in command.elements.items():
            if req.element_type == "job_instances":
                target = layout.window_definition.job_instances
            elif req.element_type == "queues":
                target = layout.window_definition.queues
            elif req.element_type == "sub_groups":
                target = layout.window_definition.sub_groups
            elif req.element_type == "items":
                target = layout.window_definition.items
            elif req.element_type == "external_groups":
                target = layout.window_definition.external_groups

            target[element_id].x = req.position_definition.x
            target[element_id].y = req.position_definition.y

        return await self.central_api.execute(LayoutDefinitionCrud.update(layout, layout.resource_id))
    
    def __reduce__(self):
        return functools.partial(GuiExtraApi, central_api=self.central_api, external_api=self.external_api), tuple()
