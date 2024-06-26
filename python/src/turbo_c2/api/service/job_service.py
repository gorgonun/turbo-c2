import asyncio
from fastapi import HTTPException
from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.api.domain.dto.job.create_job_group_request import CreateJobGroupRequest
from turbo_c2.api.domain.dto.job.job_instance_data_request import JobInstanceDataRequest
from turbo_c2.api.domain.dto.job.position_definition_request import PositionDefinitionRequest
from turbo_c2.domain.gui.layout_grid_response import LayoutGridResponse
from turbo_c2.exceptions.exceptions import JobDefinitionAlreadyExists
from turbo_c2.extra_api.command.group.get_job_group_with_instances_command import (
    GetJobGroupWithInstancesCommand,
)
from turbo_c2.extra_api.command.group.group_crud import GroupCrud
from turbo_c2.extra_api.command.group.list_subgroups_command import ListSubgroupsCommand
from turbo_c2.extra_api.command.gui.generate_layout_definition_for_group_command import (
    GenerateLayoutDefinitionForGroupCommand,
)
from turbo_c2.extra_api.command.gui.get_layout_definition_by_group_command import (
    GetLayoutDefinitionByGroup,
)
from turbo_c2.extra_api.command.gui.move_elements_command import MoveElementsCommand
from turbo_c2.extra_api.command.job.create_external_job_instance_command import (
    CreateExternalJobInstanceCommand,
)
from turbo_c2.extra_api.command.job.job_controller_crud_cr import JobControllerCrudCR
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.extra_api.command.job.job_instance_crud import JobInstanceCrud
from turbo_c2.extra_api.command.job.manage_job_command import ManageJobCommand
from turbo_c2.extra_api.command.job.scale_job_command import ScaleJobCommand
from turbo_c2.extra_api.command.queue.get_queues_command import GetQueuesCommand
from turbo_c2.helpers.serde.dynamic_job_definition_serde import DynamicJobDefinitionSerDe
from turbo_c2.helpers.serde.elements_definition_serde import LayoutGridResponseSerDe
from turbo_c2.interfaces.api import Api
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.queues.queue_reference import QueueReference


class JobService(Api, NeedsCentralApi):
    async def scale_job(self, job_instance_id: str, replicas: int):
        job_api = await self.central_api.execute(
            JobControllerCrudCR.get(job_instance_id)
        )

        if not job_api:
            raise HTTPException(
                status_code=422, detail=f"Job {job_instance_id} not found"
            )

        return await self.central_api.execute(
            ScaleJobCommand(instance_id=job_instance_id, replicas=replicas)
        )

    async def list_jobs(self):
        jobs: list[JobApi] = await self.central_api.execute(JobInstanceCrud.get())
        return [await job.get_name() for job in jobs]
    
    async def list_groups(self, src_path: str | None):
        groups = await self.central_api.execute(ListSubgroupsCommand(src_path))
        return [group.path for group in groups]

    async def get_group(self, group_path: str):
        group = await self.central_api.execute(
            GetJobGroupWithInstancesCommand(group_path=group_path)
        )

        if not group:
            raise HTTPException(status_code=422, detail=f"Group {group_path} not found")
        
        instances_data = {}

        for instance in group.job_instances:
            job_api: JobApi = await self.central_api.execute(JobControllerCrudCR.get(instance.resource_id))

            if not job_api:
                raise HTTPException(
                    status_code=422, detail=f"Job {instance.resource_id} not found"
                )
            
            instances_data[instance.resource_id] = {"state": await job_api.get_state()}

        subgroups = await self.central_api.execute(ListSubgroupsCommand(group_path))
        subgroups_with_instances = await asyncio.gather(
            *[
                self.central_api.execute(
                    GetJobGroupWithInstancesCommand(group_path=sg.path)
                )
                for sg in subgroups
            ]
        )

        layout = await self.central_api.execute(
            GetLayoutDefinitionByGroup(group_path=group_path)
        )

        if not layout:
            layout = await self.central_api.execute(
                GenerateLayoutDefinitionForGroupCommand(group_path=group.path)
            )

        elements = LayoutGridResponse(
            group=group,
            subgroups={sg.path: sg for sg in subgroups_with_instances},
            layout_definition=layout,
            instance_data=instances_data
        )

        return LayoutGridResponseSerDe.to_dict(elements, instances_data)

    async def move_element(
        self, elements: dict[str, PositionDefinitionRequest], layout_id: str
    ):
        return await self.central_api.execute(
            MoveElementsCommand(elements=elements, layout_id=layout_id)
        )

    async def list_definitions(self):
        result = [
            DynamicJobDefinitionSerDe.to_dict(job_definition)
            for job_definition in await self.central_api.execute(
                JobDefinitionCrud.get()
            )
        ]

        return result

    async def create_job_instance(
        self, job_instance_data_request: JobInstanceDataRequest
    ):
        def queue_name_to_reference(queue_name: str | None):
            return QueueReference(queue_name) if queue_name else None

        job_definition: DynamicJobDefinition = await self.central_api.execute(
            JobDefinitionCrud.get(job_instance_data_request.job_definition_id)
        )

        if not job_definition:
            raise ValueError(
                f"Job definition {job_instance_data_request.job_definition_id} does not exist"
            )

        fixed_parameters = None

        if job_definition.spec.parameters:
            if not job_instance_data_request.parameters:
                raise ValueError(
                    f"Job definition {job_instance_data_request.job_definition_id} has parameters, but none were provided"
                )

            fixed_parameters = job_definition.spec.parameters.model_validate(
                job_instance_data_request.parameters
            )

        job_instance_data = JobInstanceData(
            job_definition_id=job_instance_data_request.job_definition_id,
            replicas=job_instance_data_request.replicas,
            replication_mode=job_instance_data_request.replication_mode,
            read_only=job_instance_data_request.read_only,
            group_path=job_instance_data_request.group_path,
            input_queue_reference=queue_name_to_reference(
                job_instance_data_request.input_queue_reference
            ),
            extra_queues_references=[
                QueueReference(queue_name)
                for queue_name in job_instance_data_request.extra_queues_references
            ],
            output_queues_references=[
                QueueReference(queue_name)
                for queue_name in job_instance_data_request.output_queues_references
            ],
            parameters=fixed_parameters,
            name=job_instance_data_request.name,
        )

        try:
            return await self.central_api.execute(
                CreateExternalJobInstanceCommand(
                    job_instance_data=job_instance_data,
                    position_definition=job_instance_data_request.position_definition,
                    layout_id=job_instance_data_request.layout_id,
                )
            )
        except JobDefinitionAlreadyExists:
            raise HTTPException(
                status_code=422,
                detail=f"Job {job_instance_data_request.name} already exists",
            )

    async def create_job_group(self, create_job_group_request: CreateJobGroupRequest):
        return await self.central_api.execute(
            GroupCrud.create(
                definition=JobGroup(
                    name=create_job_group_request.name,
                    path=create_job_group_request.path,
                    description=create_job_group_request.description,
                    read_only=create_job_group_request.read_only,
                    meta=create_job_group_request.meta or {},
                ),
                resource_id=create_job_group_request.path,
            )
        )
    
    async def list_queues(self):
        queue_apis = await self.central_api.execute(GetQueuesCommand())

        return [await queue_api.get_queue_name() for queue_api in queue_apis]

    async def pause_job(self, job_instance_id: str):
        await self.central_api.execute(ManageJobCommand(job_instance_id, instruction="pause"))

    async def resume_job(self, job_instance_id: str):
        await self.central_api.execute(ManageJobCommand(job_instance_id, instruction="resume"))
