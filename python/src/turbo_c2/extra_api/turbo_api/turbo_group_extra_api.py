import asyncio
import functools
from typing import TypeVar
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.extra_api.command.group.add_job_instance_to_group_command import (
    AddJobInstanceToGroupCommand,
)
from turbo_c2.extra_api.command.group.get_groups_by_instances_command import (
    GetGroupsByInstancesCommand,
)
from turbo_c2.extra_api.command.group.get_job_group_with_instances_command import (
    GetJobGroupWithInstancesCommand,
)
from turbo_c2.extra_api.command.group.group_creator_definition import GroupCreatorDefinition
from turbo_c2.extra_api.command.group.group_crud import GroupCrud
from turbo_c2.extra_api.command.group.group_enum import GroupEnum
from turbo_c2.extra_api.command.group.list_subgroups_command import ListSubgroupsCommand
from turbo_c2.extra_api.command.group.merge_create_job_group_command import (
    MergeCreateJobGroupCommand,
)
from turbo_c2.extra_api.command.job.job_controller_crud_cr import JobControllerCrudCR
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.interfaces.extra_api import ExtraApi
from turbo_c2.interfaces.job_api import JobApi


Definition = TypeVar("Definition", bound=JobGroup)
Resource = TypeVar("Resource", bound=JobGroup)


class GroupExtraApi(DefaultExtraApiWithSubApis):
    def __init__(self, central_api: CentralApiApi | None = None) -> None:
        self.__apis: list[DefinitionResourceApi | CrudResourceApi] = [
            DefinitionResourceApi(GroupCreatorDefinition),
            CrudResourceApi(
                GroupCrud,
                creators_keys=GroupCreatorDefinition.get_api_reference().complete_id_path,
            ),
        ]
        super().__init__(
            self.__apis,
            [
                (AddJobInstanceToGroupCommand, self.add_job_instance_to_group),
                (MergeCreateJobGroupCommand, self.merge_create_job_group),
                (ListSubgroupsCommand, self.list_subgroups),
                (GetJobGroupWithInstancesCommand, self.get_group_with_instances),
                (GetGroupsByInstancesCommand, self.get_groups_by_instances),
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            GroupEnum.API_ID.value,
            central_api=central_api,
        )
        self.__lock = asyncio.Lock()

    @property
    def complete_path(self):
        return [GroupCrud.api_identifier, GroupCrud.api_path]

    async def add_job_instance_to_group(self, command: AddJobInstanceToGroupCommand):
        async with self.__lock:
            group: JobGroup = await self.central_api.execute(GroupCrud.get(command.group_path))
            if not group:
                raise ValueError(f"Group {command.group_path} does not exist")

            group.job_instances.append(command.job_instance.resource_id)

            return await self.central_api.execute(
                GroupCrud.update(resource=group, resource_id=command.group_path)
            )

    async def merge_create_job_group(self, command: MergeCreateJobGroupCommand):
        async with self.__lock:
            group: JobGroup = await self.central_api.execute(GroupCrud.get(command.group_path))
            if not group:
                group = await self.central_api.execute(
                    GroupCrud.create(command.group, command.group_path)
                )

            has_same_name = group.name == command.group.name
            matches_read_only = group.read_only == command.group.read_only

            if not has_same_name or not matches_read_only:
                raise ValueError(
                    f"Group {command.group_path} already exists with different name or read_only"
                )

            group.job_instances.extend(command.group.job_instances)
            group.meta.update(command.group.meta)

            return await self.central_api.execute(
                GroupCrud.update(resource=group, resource_id=command.group_path)
            )

    async def list_subgroups(self, command: ListSubgroupsCommand):
        list_groups = await self.central_api.execute(GroupCrud.get(prefix=command.group_path))

        return [group for group in list_groups if group.path != command.group_path]

    async def get_group_with_instances(self, command: GetJobGroupWithInstancesCommand):
        group: JobGroup = await self.central_api.execute(GroupCrud.get(command.group_path))
        if not group:
            raise ValueError(f"Group {command.group_path} does not exist")

        apis: list[JobApi] = await asyncio.gather(
            *[
                self.central_api.execute(JobControllerCrudCR.get(instance_id))
                for instance_id in group.job_instances
            ]
        )

        instances = await asyncio.gather(*[api.get_job_instance() for api in apis])

        return JobGroupWithInstances(
            group_resource_id=group.resource_id,
            name=group.name,
            path=group.path,
            description=group.description,
            job_instances=instances,
            read_only=group.read_only,
            meta=group.meta,
        )

    async def get_groups_by_instances(
        self, command: GetGroupsByInstancesCommand
    ) -> list[JobGroup]:
        result = []

        for instance_id in command.instance_ids:
            result.append(
                await self.central_api.execute(
                    GroupCrud.get(prefix=f"job_instances/${instance_id}")
                )
            )

        return result
    
    def __reduce__(self):
        return functools.partial(GroupExtraApi, central_api=self.central_api), tuple()
