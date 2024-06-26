import asyncio
from dataclasses import replace
import inspect
from itertools import chain
import os
from typing import Any, Coroutine

from fastapi import FastAPI
import ray
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.api.controller.job_controller import create_turbo_job_deployment
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.clients.prometheus.prometheus_metrics_client import PrometheusMetricsClient
from turbo_c2.clients.prometheus.remote_prometheus_metrics_api import (
    RemotePrometheusMetricsApi,
)
from turbo_c2.decorators.actor import ActorDefinition, actor
from turbo_c2.decorators.controller import controller
from turbo_c2.decorators.extra_api import extra_api
from turbo_c2.domain.job.new_job_created import NewJobCreated
from turbo_c2.domain.scheduler.waitable_item import WaitableItem
from turbo_c2.extra_api.command.external_api.get_external_apis_mapping_command import (
    GetExternalApisMappingCommand,
)
from turbo_c2.extra_api.command.group.group_crud import GroupCrud
from turbo_c2.extra_api.command.job.job_api_definition import JobApiDefinition
from turbo_c2.extra_api.command.job.job_controller_definition import JobControllerDefinition
from turbo_c2.extra_api.command.job.job_creator_definition import JobCreatorDefinition
from turbo_c2.extra_api.command.job.job_definition_crud import JobDefinitionCrud
from turbo_c2.extra_api.command.job.job_controller_crud_cr import JobControllerCrudCR
from turbo_c2.extra_api.command.job.job_instance_crud import JobInstanceCrud
from turbo_c2.extra_api.command.job.job_type_definition import JobTypeDefinition
from turbo_c2.extra_api.command.queue.create_queue_command import CreateQueueCommand
from turbo_c2.extra_api.command.queue.set_queue_api_command import SetQueueApiCommand
from turbo_c2.extra_api.command.queue.set_queue_configuration_command import (
    SetQueueConfigurationCommand,
)
from turbo_c2.extra_api.command.queue.set_queue_controller_command import (
    SetQueueControllerCommand,
)
from turbo_c2.extra_api.command.queue.set_queue_creator_command import SetQueueCreatorCommand
from turbo_c2.extra_api.command.queue.set_queue_type_command import SetQueueTypeCommand
from turbo_c2.decorators.queue import queue
from turbo_c2.extra_api.turbo_api.turbo_in_memory_object_storage_extra_api import InMemoryObjectStorageExtraApi
from turbo_c2.extra_api.turbo_api.turbo_object_storage_extra_api import ObjectStorageExtraApi
from turbo_c2.globals.ebf_definitions import setup
from turbo_c2.helpers.async_utils import amap
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.external_api import ExternalApi
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_definition import JobDefinition
from turbo_c2.interfaces.needs_load import NeedsLoad
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.needs_central_api import NeedsCentralApi
from turbo_c2.scheduler.lazy_definable import LazyDefinable
from turbo_c2.scheduler.lazy_scheduler_parameters import LazySchedulerParameters
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.globals.ebf_global import get_scheduler_globals, get_scheduler_globals_object
from turbo_c2.helpers.turbo_logger import TurboLogger
from ray import serve
from fastapi.middleware.cors import CORSMiddleware


def get_global_error_queue_definition():
    @queue(for_types=[Exception])
    def global_error_queue():
        return QueueDefinition(
            "global_error_queue", meta={"created_by": "default_scheduler"}
        )

    return global_error_queue


def get_new_job_queue_definition():
    @queue(for_types=[NewJobCreated])
    def new_job_queue():
        return QueueDefinition(
            "new_job_queue", meta={"created_by": "default_scheduler"}
        )

    return new_job_queue


def get_new_waitable_items_definition():
    @queue(for_types=[WaitableItem])
    def new_waitable_item_queue():
        return QueueDefinition(
            "new_waitable_item_queue", meta={"created_by": "default_scheduler"}
        )

    return new_waitable_item_queue


@actor(
    name="prometheus",
    api_path="client",
    api_identifier="metrics",
    api=RemotePrometheusMetricsApi,
)
async def get_prometheus_metrics_client():
    return ActorDefinition(actor_class=PrometheusMetricsClient)


@extra_api()
def get_object_storage_extra_api(
    central_api: CentralApi, mapping: dict[str, ExternalApi]
):
    return (
        ObjectStorageExtraApi(
            object_storage_api_name="local_storage",
            json_object_storage_api_name="json_local_storage",
            external_apis=mapping,
            central_api=central_api,
        ),
        None,
    )


@extra_api()
def get_in_memory_object_storage_extra_api(
    central_api: CentralApi, _: dict[str, ExternalApi]
):
    return (
        InMemoryObjectStorageExtraApi(
            central_api=central_api,
        ),
        None,
    )


@controller(name="turbo", route_prefix="/api/v1")
def get_job_controller(app: FastAPI, central_api: CentralApi):
    return create_turbo_job_deployment(app, central_api)


class DefaultScheduler:
    @classmethod
    async def prepare_job_group(
        cls,
        central_api: CentralApi,
        job_group: JobGroupWithInstances,
        scheduler_queues: dict[str, Any],
        logger: TurboLogger,
    ):
        job_apis_cr: list[Coroutine[Any, Any, list[JobApi]]] = []

        logger.info(f"Creating group {job_group.path}")
        created_group = await central_api.execute(GroupCrud.get(job_group.path))

        if not created_group:
            created_group = await central_api.execute(
                GroupCrud.create(replace(job_group, job_instances=[]), job_group.path)
            )

        logger.info(f"Creating job instances for group {job_group.path}")

        job_apis_cr.extend(
            [
                cls.prepare_job_controller(
                    central_api,
                    job_instance,
                    created_group.path,
                    scheduler_queues,
                    logger,
                )
                for job_instance in job_group.job_instances
            ]
        )

        return created_group, chain.from_iterable(
            await asyncio.gather(*[job_apis for job_apis in job_apis_cr])
        )

    @staticmethod
    async def prepare_job_controller(
        central_api: CentralApi,
        job_instance: JobInstance,
        group_path: str,
        scheduler_queues: dict[str, Any],
        logger: TurboLogger,
    ):
        async def prepare_job_api(job_api: JobApi):
            logger.info("Adding central api to job api")
            await job_api.add_central_api(central_api)

            logger.info("Evaluating queues for job")
            await job_api.evaluate_queues(scheduler_queues)

            logger.info("Updating job instance")
            await central_api.execute(
                JobControllerCrudCR.update(
                    job_api.job_controller,
                    (await job_api.get_job_instance()).resource_id,
                )
            )

            return job_api

        job_apis: list[JobApi] = []

        job_definition: JobDefinition = await central_api.execute(
            JobDefinitionCrud.create(
                job_instance.job_definition,
                job_instance.job_definition.resource_id,
            )
        )

        job_instance_data = JobInstanceData(
            job_definition_id=job_definition.resource_id,
            replicas=job_instance.replicas,
            replication_mode=job_instance.replication_mode,
            read_only=job_instance.read_only,
            input_queue_reference=job_instance.input_queue_reference,
            extra_queues_references=job_instance.extra_queues_references,
            output_queues_references=job_instance.output_queues_references,
            parameters=job_instance.parameters,
            name=job_instance.name or job_definition.name,
            group_path=group_path,
            num_cpus=job_instance.num_cpus,
            memory=job_instance.memory,
            scheduling_strategy=job_instance.scheduling_strategy,
        )

        logger.debug("Creating job instance", job_instance_data)
        job_instances: list[JobInstance] = await central_api.execute(
            JobInstanceCrud.create(job_instance_data)
        )

        job_apis_cr = [
            central_api.execute(
                JobControllerCrudCR.create(job_instance, job_instance.resource_id)
            )
            for job_instance in job_instances
        ]

        prepared_job_apis_cr = amap(prepare_job_api, job_apis_cr)

        async for job_api_cr in prepared_job_apis_cr:
            job_api = await job_api_cr
            job_apis.append(job_api)

        return job_apis

    @classmethod
    async def create(
        self,
        *lazy_scheduler_definables: LazyDefinable,
        mode: str | None = None,
        central_api: DefaultCentralApi | None = None,
        create_global_error_queue: bool = True,
        environment_variables: dict[str, str] | None = None,
    ):
        logger = TurboLogger("DefaultScheduler")

        runtime_env = {
            "env_vars": environment_variables or {},
        }

        ray.init(_metrics_export_port=8080, runtime_env=runtime_env)

        logger.info("Setting up default scheduler")
        setup(get_scheduler_globals_object())

        new_job_queue = get_new_job_queue_definition()
        new_waitable_item_queue = get_new_waitable_items_definition()
        default_queues = [new_job_queue, new_waitable_item_queue]

        if create_global_error_queue:
            default_queues.append(get_global_error_queue_definition())

        mode = mode or get_scheduler_globals().config.mode
        logger.info(f"Using mode {mode}")

        central_api = central_api or get_scheduler_globals().default_central_api()

        logger.info("Setting up central api for queue")
        queue_creator = get_scheduler_globals().default_queue_creator()("default")
        queue_creator.add_central_api(central_api)

        logger.info("Setting up central api for job")
        job_creator = get_scheduler_globals().default_job_creator()("default")
        job_creator.add_central_api(central_api)

        scheduler = get_scheduler_globals().scheduler_mode_mapping[mode]

        logger.info("Setting up extra apis")
        extra_apis_with_central_api = []

        for extra_apis in get_scheduler_globals().get_extra_apis():
            extra_apis.add_central_api(central_api)
            extra_apis_with_central_api.append(extra_apis)

        await asyncio.gather(
            *[
                central_api.put_extra_api(extra_apis)
                for extra_apis in extra_apis_with_central_api
            ]
        )

        for path, (
            external_definition_command,
            kwargs,
        ) in get_scheduler_globals().get_resource_mappings(
            prefix="external_api", matches="external_api/.*/init"
        ):
            logger.info(f"Setting up init command {path} for external apis")
            await central_api.execute(external_definition_command(**kwargs))

        mapping = await central_api.execute(GetExternalApisMappingCommand())

        for path, resource in get_scheduler_globals().get_resource_mappings(
            prefix="init/extra_api_constructor"
        ):
            new_extra_api = await resource(central_api, mapping)
            logger.info(f"Set new extra api {new_extra_api}")

        await asyncio.gather(
            *[
                central_api.execute(SetQueueCreatorCommand(queue_creator)),
                central_api.execute(
                    SetQueueControllerCommand(
                        get_scheduler_globals().queue_controller(), "default"
                    )
                ),
                central_api.execute(
                    SetQueueApiCommand(get_scheduler_globals().queue_api(), "default")
                ),
            ],
            *[
                central_api.execute(
                    SetQueueTypeCommand(queue_type, definition_type, queue_id)
                )
                for definition_type, (queue_type, queue_id) in (
                    get_scheduler_globals().queue_type_mapping().items()
                )
            ],
            *[
                central_api.execute(
                    JobCreatorDefinition.set(
                        resource=job_creator, resource_id="default"
                    )
                ),
                central_api.execute(
                    JobControllerDefinition.set(
                        get_scheduler_globals().job_controller(), "default"
                    )
                ),
                central_api.execute(
                    JobApiDefinition.set(get_scheduler_globals().job_api(), "default")
                ),
            ],
        )

        logger.info("Adding central api to objects")
        for path, resource in get_scheduler_globals().get_resource_mappings(
            prefix="init/needs_central_api"
        ):
            if isinstance(resource, NeedsCentralApi):
                logger.info(f"Adding central api to {resource}")
                resource.add_central_api(central_api)

            elif inspect.iscoroutinefunction(resource):
                logger.info(f"Adding central api to function resource {path}")
                await resource(central_api)

        logger.info("Setting up job definitions")
        for definition_type, (job_type, _) in (
            get_scheduler_globals().get_job_definition_mapping().items()
        ):
            await central_api.execute(JobTypeDefinition.set(job_type, definition_type))

        for path, (
            external_definition_command,
            kwargs,
        ) in get_scheduler_globals().get_resource_mappings(
            prefix="extra_api_definition", matches="extra_api_definition/.*/init"
        ):
            logger.info(f"Setting up init command {path} for extra apis")
            await central_api.execute(external_definition_command(**kwargs))

        for path, (
            client_definition_command,
            kwargs,
        ) in get_scheduler_globals().get_resource_mappings(
            prefix="client", matches="client/.*/init"
        ):
            logger.info(f"Setting up init command {path} for clients")
            await central_api.execute(client_definition_command(**kwargs))

        lazy_scheduler_definables_jobs = []
        lazy_scheduler_definables_queues = []

        for lazy_scheduler_definable in lazy_scheduler_definables:
            lazy_scheduler_definables_queues.extend(
                lazy_scheduler_definable.get_queues()
            )

        scheduler_queues: dict[str, Any] = {}

        logger.info("Creating queues")
        for queue in (
            get_scheduler_globals().get_queues()
            + lazy_scheduler_definables_queues
            + default_queues
        ):
            if not scheduler_queues.get(queue.name):
                scheduler_queues[queue.name] = await central_api.execute(
                    CreateQueueCommand(queue)
                )
                for configuration in queue.meta.get("configuration", []):
                    await central_api.execute(
                        SetQueueConfigurationCommand(
                            configuration["path"], configuration["value"]
                        )
                    )

        logger.info("Setting up lazy scheduler definables")
        for lazy_scheduler_definable in lazy_scheduler_definables:
            remote_objects_instances = lazy_scheduler_definable.get_remote_objects()
            remote_objects = {}

            for (
                remote_object_instance_name,
                remote_object_instance,
            ) in remote_objects_instances.items():
                remote_objects[remote_object_instance_name] = (
                    await central_api.put_remote_object_reference(
                        [lazy_scheduler_definable.name, remote_object_instance_name],
                        remote_object_instance,
                    )
                )

            logger.debug("Setting up lazy scheduler definable")
            scheduler_definitions = await lazy_scheduler_definable.setup(
                LazySchedulerParameters(
                    config=get_scheduler_globals().config,
                    central_api=central_api,
                    ebf_globals=get_scheduler_globals(),
                    remote_objects=remote_objects,
                    queues=scheduler_queues,
                )
            )
            logger.debug(f"Setting {len(scheduler_definitions.jobs)} jobs")
            lazy_scheduler_definables_jobs.extend(scheduler_definitions.jobs)

            logger.debug(f"Settings apis: {len(scheduler_definitions.apis)}")
            for api in scheduler_definitions.apis:
                api.add_central_api(central_api)
                await central_api.put_extra_api(api)

        for (
            needs_queue_evaluation
        ) in get_scheduler_globals().get_needs_queue_evaluations():
            await needs_queue_evaluation.evaluate_queues(scheduler_queues)

        jobs = []

        for _, job_group in get_scheduler_globals().get_job_groups():
            _, job_apis = await self.prepare_job_group(
                central_api, job_group, scheduler_queues, logger
            )
            jobs.extend(job_apis)

        logger.info("Loading resources")
        for _, resource in get_scheduler_globals().get_resource_mappings(
            prefix="init/load"
        ):
            if isinstance(resource, NeedsLoad):
                await resource.load()

        get_scheduler_globals().set_remote_only(True)
        get_scheduler_globals().set_central_api(central_api)

        prometheus_client_actor_definition = await central_api.get_object_reference(
            ["resource_creator", "actor", "metrics", "client", "prometheus"]
        )

        if not prometheus_client_actor_definition:
            raise RuntimeError("Prometheus client actor not found")

        metrics_client = prometheus_client_actor_definition.actor_ref
        deployments = []

        allowed_origins = [
                f"http://localhost",
                f"http://localhost:5173",
                f"http://localhost:5174",
        ]

        custom_host = os.environ.get("CUSTOM_HOST")
        if custom_host:
            allowed_origins.extend([
                f"{custom_host}",
                f"{custom_host}:5173",
                f"{custom_host}:5174",
            ])

        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        for _, resource in get_scheduler_globals().get_resource_mappings(
            prefix="init/deployment_constructor"
        ):
            deployment, run_args, run_kwargs, name = resource(app, central_api)
            deployments.append(
                {
                    "deployment": deployment,
                    "run_args": run_args,
                    "run_kwargs": run_kwargs,
                    "name": name,
                }
            )

        for deployment in deployments:
            serve.run(
                deployment["deployment"].bind(),
                *deployment["run_args"],
                **deployment["run_kwargs"],
                name=deployment["name"],
            )

        return (
            scheduler(
                jobs, scheduler_queues[new_job_queue.name], scheduler_queues[new_waitable_item_queue.name], central_api, metrics_client
            ),
            central_api,
        )
