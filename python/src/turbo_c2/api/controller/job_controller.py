from typing import Annotated
from fastapi import Depends, FastAPI
from turbo_c2.api.domain.dto.job.create_job_group_request import CreateJobGroupRequest
from turbo_c2.api.domain.dto.job.job_instance_data_request import JobInstanceDataRequest
from turbo_c2.api.domain.dto.job.position_definition_request import PositionDefinitionRequest
from turbo_c2.api.domain.dto.job.scale_job_request import ScaleJobRequest
from turbo_c2.api.service.job_service import JobService
from turbo_c2.api.service.metrics_service import MetricsService
from turbo_c2.interfaces.central_api import CentralApi


def create_turbo_job_deployment(app: FastAPI, central_api: CentralApi):
    class TurboControllerDeployment:

        @app.get("/queues")
        async def list_queues(
            self,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.list_queues()

        @app.post("/jobs/{job_id}/scale")
        async def scale_job(
            self,
            job_id: str,
            body: ScaleJobRequest,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.scale_job(job_id, body.replicas)

        @app.get("/jobs")
        async def get_jobs(
            self,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.list_jobs()

        @app.get("/groups")
        async def list_groups(
            self,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
            src_path: str | None = None,
        ):
            return await job_service.list_groups(src_path)
        
        @app.get("/groups/{group_path}")
        async def get_group(
            self,
            group_path: str,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.get_group(group_path)

        @app.get("/definitions")
        async def list_definitions(
            self,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.list_definitions()
        
        @app.put("/layouts/{layout_id}/move_elements")
        async def move_elements(
            self,
            layout_id: str,
            elements: dict[str, PositionDefinitionRequest],
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.move_element(elements, layout_id)
        
        @app.post("/groups")
        async def create_group(
            self,
            create_job_group_request: CreateJobGroupRequest,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.create_job_group(create_job_group_request)
        
        @app.post("/job_instances")
        async def create_job_instance(
            self,
            job_instance_data_request: JobInstanceDataRequest,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.create_job_instance(job_instance_data_request)
        
        @app.put("/job_instances/{job_instance_id}/pause")
        async def pause_job_instance(
            self,
            job_instance_id: str,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.pause_job(job_instance_id)
        
        @app.put("/job_instances/{job_instance_id}/resume")
        async def resume_job_instance(
            self,
            job_instance_id: str,
            job_service: Annotated[
                JobService,
                Depends(
                    lambda: JobService(central_api)
                ),
            ],
        ):
            return await job_service.resume_job(job_instance_id)
        
        @app.get("/metrics/queues/{queue_name}/aggregated")
        async def get_aggregated_metrics_by_queue(
            self,
            queue_name: str,
            metrics_service: Annotated[
                MetricsService,
                Depends(
                    lambda: MetricsService(central_api)
                ),
            ],
            time: str | None = None,
        ):
            return await metrics_service.get_aggregated_metrics_by_queue(queue_name, time)
        
        @app.get("/metrics/groups/{group_path}/aggregated")
        async def get_aggregated_metrics_by_group(
            self,
            group_path: str,
            metrics_service: Annotated[
                MetricsService,
                Depends(
                    lambda: MetricsService(central_api)
                ),
            ],
            time: str | None = None,
        ):
            return await metrics_service.get_aggregated_metrics_by_group(group_path, time)
        
        
    return TurboControllerDeployment
