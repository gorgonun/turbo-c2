import asyncio
from dataclasses import replace
import functools
import json
from typing import cast

from pydantic import BaseModel
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.domain.gui.external_job_group_definition import ExternalJobGroupDefinition
from turbo_c2.domain.gui.layout_definition import JobInstancePositionDefinition
from turbo_c2.domain.job.job_instance_data_with_id import JobInstanceDataWithId
from turbo_c2.domain.job.new_job_created import NewJobCreated
from turbo_c2.exceptions.exceptions import JobDefinitionAlreadyExists
from turbo_c2.external_api.local_storage_external_api import LocalStorageExternalApi
from turbo_c2.extra_api.command.group.add_job_instance_to_group_command import (
    AddJobInstanceToGroupCommand,
)
from turbo_c2.extra_api.command.group.external_job_group_definition_resource import (
    ExternalJobGroupDefinitionResource,
)
from turbo_c2.extra_api.command.gui.add_new_element_command import AddNewElementCommand
from turbo_c2.extra_api.command.job.create_external_job_instance_command import (
    CreateExternalJobInstanceCommand,
)
from turbo_c2.extra_api.command.job.job_api_definition import JobApiDefinition
from turbo_c2.extra_api.command.job.job_controller_creator_definition import (
    JobControllerCreatorDefinition,
)
from turbo_c2.extra_api.command.job.job_controller_definition import JobControllerDefinition
from turbo_c2.extra_api.command.job.job_creator_definition import JobCreatorDefinition
from turbo_c2.extra_api.command.job.job_definition_creator_definition import (
    JobDefinitionCreatorDefinition,
)
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.extra_api.command.job.job_controller_crud_cr import (
    JobControllerCrudCR,
)
from turbo_c2.extra_api.command.job.job_enum import JobEnum
from turbo_c2.extra_api.command.job.job_instance_creator_definition import (
    JobInstanceCreatorDefinition,
)
from turbo_c2.extra_api.command.job.job_instance_crud import (
    CreateInstanceByDefinitionIdCommand,
    JobInstanceCrud,
)
from turbo_c2.extra_api.command.job.job_type_definition import JobTypeDefinition
from turbo_c2.extra_api.command.job.manage_job_command import ManageJobCommand
from turbo_c2.extra_api.command.job.scale_job_command import ScaleJobCommand
from turbo_c2.extra_api.command.queue.create_queue_command import CreateQueueCommand
from turbo_c2.extra_api.command.queue.get_queues_by_type_command import GetQueuesByTypeCommand
from turbo_c2.extra_api.crud_client_resource_api import CrudClientResourceApi
from turbo_c2.extra_api.crud_resource_api import CrudResourceApi
from turbo_c2.extra_api.default_extra_api_with_sub_apis import DefaultExtraApiWithSubApis
from turbo_c2.extra_api.definition_resource_api import DefinitionResourceApi
from turbo_c2.extra_api.resource_api import ResourceApi
from turbo_c2.helpers.serde.dynamic import ExternalJobGroupDefinitionSerDe
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.needs_load import NeedsLoad
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.needs_external_api import NeedsExternalApi
from turbo_c2.jobs.node_representation import NodeRepresentation
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.queues.queue_reference import QueueReference


# FIXME: NeedsExternalApi is really needed?
class JobExtraApi(
    DefaultExtraApiWithSubApis, NeedsExternalApi[LocalStorageExternalApi], NeedsLoad
):
    def __init__(self, central_api: CentralApiApi | None = None, external_api: LocalStorageExternalApi | None = None) -> None:
        self.job_instance_crud = CrudResourceApi(
            JobInstanceCrud,
            creators_keys=JobInstanceCreatorDefinition.get_api_reference().complete_id_path,
            exclude_commands=["create"],
        )
        self.external_job_group_definition_api = ResourceApi(
            ExternalJobGroupDefinitionResource,
            before_write=lambda e: ExternalJobGroupDefinitionSerDe.serialize(e).encode(
                "utf-8"
            ),
            after_read=lambda eb: ExternalJobGroupDefinitionSerDe.deserialize(
                eb.decode("utf-8")
            ),
        )

        self.__apis = [
            DefinitionResourceApi(JobControllerDefinition),
            DefinitionResourceApi(JobApiDefinition),
            DefinitionResourceApi(JobCreatorDefinition),
            DefinitionResourceApi(JobTypeDefinition),
            DefinitionResourceApi(JobDefinitionCreatorDefinition),
            DefinitionResourceApi(JobInstanceCreatorDefinition),
            DefinitionResourceApi(JobControllerCreatorDefinition),
            CrudResourceApi(
                JobDefinitionCrud,
                creators_keys=JobDefinitionCreatorDefinition.get_api_reference().complete_id_path,
            ),
            CrudClientResourceApi(
                JobControllerCrudCR,
                creators_keys=JobControllerCreatorDefinition.get_api_reference().complete_id_path,
                apis_keys=JobApiDefinition.get_api_reference().complete_id_path,
            ),
            self.job_instance_crud,
            self.external_job_group_definition_api,
        ]
        super().__init__(
            self.__apis,
            [
                (ScaleJobCommand, self.scale_job),
                (JobInstanceCrud.create_command_path(), self.create_job_instance),
                (CreateExternalJobInstanceCommand, self.create_external_job_instance),
                *[
                    command
                    for api in self.__apis
                    for command in api.get_command_structure()
                ],
            ],
            JobEnum.API_ID.value,
            central_api=central_api
        )

        self.__derivated_id_to_job_instance_id_map: dict | None = None
        self.__external_group_lock = asyncio.Lock()

        if external_api:
            self.add_external_api(external_api)

    async def on_load(self):
        external_group_definitions: list[ExternalJobGroupDefinition] = (
            await self.central_api.execute(ExternalJobGroupDefinitionResource.get())
        )
        for external_group_definition in external_group_definitions:
            for job_instance in external_group_definition.job_instances_data.values():
                definition: DynamicJobDefinition = await self.central_api.execute(
                    JobDefinitionCrud.get(job_instance.job_definition_id)
                )

                if not definition:
                    continue

                if definition.spec.parameters:
                    if not job_instance.parameters:
                        raise ValueError(
                            f"Job definition {job_instance.job_definition_id} has parameters, but none were provided"
                        )

                    if isinstance(job_instance.parameters, BaseModel):
                        job_instance.parameters = (
                            definition.spec.parameters.model_construct(
                                **job_instance.parameters.model_dump()
                            )
                        )
                    else:
                        job_instance.parameters = (
                            definition.spec.parameters.model_construct(
                                **job_instance.parameters
                            )
                        )

                self.logger.debug(f"Creating job instance {job_instance}")
                new_instances = await self.create_job_instance(
                    JobInstanceCrud.create(job_instance)
                )

                for new_instance in new_instances:
                    api = await self.central_api.execute(
                        JobControllerCrudCR.create(
                            definition=new_instance,
                            resource_id=new_instance.resource_id,
                        )
                    )

                    await api.add_central_api(self.central_api)

                    not_evaluate_queues = filter(None, [new_instance.input_queue_reference] + (new_instance.extra_queues_references or []) + (new_instance.output_queues_references or []))
                    queues = {}
                    for defined_queue in not_evaluate_queues:
                        queue = await self.central_api.execute(
                            CreateQueueCommand(QueueDefinition(defined_queue), fail_if_exists=False)
                        )
                        queues[defined_queue] = queue

                    await api.evaluate_queues(queues)

                    await self.central_api.execute(
                        JobControllerCrudCR.update(
                            api.job_controller,
                            new_instance.resource_id,
                        )
                    )

    def add_external_api(self, external_api: LocalStorageExternalApi):
        self.external_job_group_definition_api.add_external_api(external_api)
        return super().add_external_api(external_api)

    async def get_derivated_id_to_job_instance_id_map(self) -> dict:
        if self.external_api and not self.__derivated_id_to_job_instance_id_map:
            derivated_id_to_job_instance_id_map_bytes = (
                await self.external_api.get_object_reference(
                    ["job_instances", "derivated_id"]
                )
            )

            if derivated_id_to_job_instance_id_map_bytes:
                self.__derivated_id_to_job_instance_id_map = json.loads(
                    derivated_id_to_job_instance_id_map_bytes.decode("utf-8")
                )

            else:
                self.__derivated_id_to_job_instance_id_map = {}

        elif not self.external_api:
            raise ValueError("External API not set")

        return self.__derivated_id_to_job_instance_id_map

    async def set_derivated_id_to_job_instance_id_key(self, key: str, value: str):
        derivated_id_to_job_instance_id_map = (
            await self.get_derivated_id_to_job_instance_id_map()
        )
        derivated_id_to_job_instance_id_map[key] = value

        if self.external_api:
            await self.external_api.put_remote_object_reference(
                ["job_instances", "derivated_id"],
                json.dumps(derivated_id_to_job_instance_id_map).encode("utf-8"),
            )
        else:
            raise ValueError("External API not set")

    async def scale_job(self, command: ScaleJobCommand):
        job = await self.central_api.execute(JobControllerCrudCR.get(command.instance_id))
        if not job:
            raise ValueError(f"Job {command.instance_id} does not exist")
        
        return await job.scale(command.replicas)
    

    async def manage_job(self, command: ManageJobCommand):
        job = await self.central_api.execute(JobControllerCrudCR.get(command.instance_id))
        if not job:
            raise ValueError(f"Job {command.instance_id} does not exist")
        
        if command.instruction == "pause":
            return await job.pause()
        
        if command.instruction == "resume":
            return await job.resume()

    async def create_external_job_instance(
        self, command: CreateExternalJobInstanceCommand
    ):
        def queue_reference_to_id(queue_reference: QueueReference | None):
            return queue_reference.identifier if queue_reference else None

        new_instances = await self.create_job_instance(command)
        new_instances_data_with_id = [
            JobInstanceDataWithId.model_construct(
                instance_resource_id=instance.resource_id,
                job_definition_id=instance.job_definition.resource_id,
                replicas=instance.replicas,
                replication_mode=instance.replication_mode.value,
                read_only=instance.read_only,
                group_path=instance.group_path,
                input_queue_reference=queue_reference_to_id(
                    instance.input_queue_reference
                ),
                extra_queues_references=[
                    queue_reference_to_id(x) for x in instance.extra_queues_references
                ],
                output_queues_references=[
                    queue_reference_to_id(x) for x in instance.output_queues_references
                ],
                parameters=instance.parameters,
                name=instance.name,
            )
            for instance in new_instances
        ]

        apis = []

        external_group_definition = await self.central_api.execute(
            ExternalJobGroupDefinitionResource.get(command.job_instance_data.group_path)
        )

        if not external_group_definition:
            external_job_group_definition = ExternalJobGroupDefinition.model_construct(
                resource_id=command.job_instance_data.group_path,
                name=command.job_instance_data.group_path,
                group_path=command.job_instance_data.group_path,
            )
            external_group_definition = await self.central_api.execute(
                ExternalJobGroupDefinitionResource.create(
                    definition=external_job_group_definition,
                    resource_id=external_job_group_definition.resource_id,
                )
            )

        async with self.__external_group_lock:
            external_group_definition.job_instances_data.update(
                {
                    instance.resource_id: instance
                    for instance in new_instances_data_with_id
                }
            )

            await self.central_api.execute(
                ExternalJobGroupDefinitionResource.update(
                    resource_id=external_group_definition.resource_id,
                    resource=external_group_definition,
                )
            )

            for job_instance in new_instances:
                api: JobApi = await self.central_api.execute(
                    JobControllerCrudCR.create(
                        definition=job_instance, resource_id=job_instance.resource_id
                    )
                )

                await api.add_central_api(self.central_api)

                not_evaluate_queues = filter(None, [job_instance.input_queue_reference] + (job_instance.extra_queues_references or []) + (job_instance.output_queues_references or []))
                queues = {}
                for defined_queue in not_evaluate_queues:
                    queue = await self.central_api.execute(
                        CreateQueueCommand(QueueDefinition(defined_queue.identifier), fail_if_exists=False)
                    )
                    queues[defined_queue.identifier] = queue

                await api.evaluate_queues(queues)

                await self.central_api.execute(
                    JobControllerCrudCR.update(
                        api.job_controller,
                        job_instance.resource_id,
                    )
                )

                apis.append(api)

                queues_to_send_new_job = await self.central_api.execute(GetQueuesByTypeCommand(NewJobCreated))
                await asyncio.gather(
                    *[
                        queue.put(NewJobCreated(job_api=api))
                        for queue in queues_to_send_new_job
                    ]
                )

                if command.position_definition:
                    if not command.layout_id:
                        raise ValueError(
                            "Position definition provided, but no layout id"
                        )

                    position_definition = JobInstancePositionDefinition.model_construct(
                        representation=NodeRepresentation.ACTION,
                        resource_id=job_instance.resource_id,
                        x=command.position_definition.x,
                        y=command.position_definition.y,
                        width=4,
                        height=2,
                    )

                    await self.central_api.execute(
                        AddNewElementCommand(
                            element=position_definition,
                            element_id=job_instance.resource_id,
                            layout_id=command.layout_id,
                            element_type="job_instances",
                        )
                    )

        return apis

    async def create_job_instance(self, command: CreateInstanceByDefinitionIdCommand):
        if not command.creator_id:
            creator_list = await self.job_instance_crud.list_creator_keys()
            if not creator_list:
                raise ValueError(
                    f"No creator found for create {command} on {JobDefinitionCreatorDefinition.get_api_reference().complete_id_path}"
                )

            creator_id = creator_list[0]

        creator = await self.job_instance_crud.get_creator(
            command.creator_id or creator_id
        )

        if not creator:
            raise ValueError(
                f"Creator {command.creator_id or creator_id} from command {command} does not exist"
            )

        job_instances: list[JobInstance] = await creator.create(command.job_instance_data, meta={"created_by": "/".join(self.job_instance_crud.complete_path)})  # type: ignore
        updated_instances: list[JobInstance] = []

        for job_instance in job_instances:
            job_instance_id = (
                await self.get_derivated_id_to_job_instance_id_map()
            ).get(job_instance.derivated_id)

            if job_instance_id:
                job_instance_with_id = replace(
                    job_instance, instance_resource_id=job_instance_id
                )

            else:
                job_instance_with_id = job_instance

            updated_instances.append(job_instance_with_id)

            exists_by_id = await self.central_api.execute(
                JobInstanceCrud.get(job_instance_with_id.resource_id)
            )
            exists_by_derivated_id = await self.central_api.execute(
                JobInstanceCrud.get(
                    prefix=f"derivated_id/{job_instance_with_id.derivated_id}"
                )
            )

            if exists_by_id or exists_by_derivated_id:
                if command.fail_if_exists:
                    raise JobDefinitionAlreadyExists(
                        f"Resource {job_instance_with_id.resource_id if exists_by_id else job_instance_with_id.derivated_id} already exists"
                    )
                return cast(list[JobInstance], [])

        for job_instance in updated_instances:
            await self.job_instance_crud.set(
                job_instance.resource_id,
                job_instance,
                command.fail_if_exists,
                indexes=command.indexes,
            )

            await self.set_derivated_id_to_job_instance_id_key(
                job_instance.derivated_id, job_instance.resource_id
            )

            await self.central_api.execute(
                AddJobInstanceToGroupCommand(
                    job_instance.group_path, job_instance=job_instance
                )
            )

        return updated_instances
    
    def __reduce__(self):
        return functools.partial(JobExtraApi, central_api=self.central_api, external_api=self.external_api), tuple()
