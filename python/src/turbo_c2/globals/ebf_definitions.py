import os
from typing import Any, Type

from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.clients.prometheus.prometheus_http_client import PrometheusHttpClient
from turbo_c2.config.config import DefaultConfig
from turbo_c2.domain.gui.layout_definition import LayoutDefinition
from turbo_c2.domain.gui.layout_element_command import LayoutElementCommand
from turbo_c2.external_api.json_local_storage_external_api import JsonLocalStorageExternalApi
from turbo_c2.external_api.local_storage_external_api import LocalStorageExternalApi
from turbo_c2.extra_api.command.client.client_definition import ClientDefinition
from turbo_c2.extra_api.command.external_api.external_api_definition import ExternalApiDefinition
from turbo_c2.extra_api.turbo_api import turbo_job_extra_api
from turbo_c2.extra_api import queue_extra_api
from turbo_c2.extra_api.command.group.group_creator_definition import GroupCreatorDefinition
from turbo_c2.extra_api.command.gui.layout_definition_creator_definition import LayoutDefinitionCreatorDefinition
from turbo_c2.extra_api.command.gui.layout_element_command_creator_definition import LayoutElementCommandCreatorDefinition
from turbo_c2.extra_api.command.job.job_controller_creator_definition import JobControllerCreatorDefinition
from turbo_c2.extra_api.command.job.job_definition_creator_definition import JobDefinitionCreatorDefinition
from turbo_c2.extra_api.command.job.job_instance_creator_definition import JobInstanceCreatorDefinition
from turbo_c2.extra_api.resources.group_extra_api.group_creator import GroupCreator
from turbo_c2.extra_api.resources.gui_extra_api.layout_definition_creator import LayoutDefinitionCreator
from turbo_c2.extra_api.resources.gui_extra_api.layout_element_command_creator import LayoutElementCommandCreator
from turbo_c2.extra_api.resources.job_extra_api.default_job_instance_creator import DefaultJobInstanceCreator
from turbo_c2.extra_api.resources.job_extra_api.job_definition_creator import JobDefinitionCreator
from turbo_c2.extra_api.turbo_api.turbo_client_extra_api import ClientExtraApi
from turbo_c2.extra_api.turbo_api.turbo_external_api_extra_api import ExternalApiExtraApi
from turbo_c2.extra_api.turbo_api.turbo_group_extra_api import GroupExtraApi
from turbo_c2.extra_api.turbo_api.turbo_gui_extra_api import GuiExtraApi
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_instance_data import JobInstanceData
from turbo_c2.jobs.remote_job_api import RemoteJobApi
from turbo_c2.jobs.dynamic_job.dynamic_job import DynamicJob
from turbo_c2.jobs.default_job_creator import DefaultJobCreator
from turbo_c2.jobs.job_with_queue_evaluation import JobWithQueueEvaluation
from turbo_c2.jobs.local_job_controller import LocalJobController
from turbo_c2.jobs.local_job_creator import LocalJobCreator
from turbo_c2.jobs.remote_job_controller import RemoteJobController
from turbo_c2.jobs.remote_job_controller_creator import RemoteJobControllerCreator
from turbo_c2.queue_api.remote_queue_api import RemoteQueueApi
from turbo_c2.queues.local_queue_controller import LocalQueueController
from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.queues.remote_queue_controller import RemoteQueueController
from turbo_c2.scheduler.local_scheduler import LocalScheduler
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.local_queue_creator import LocalQueueCreator
from turbo_c2.queues.queue_creator import QueueCreator
from turbo_c2.queues.remote_queue_creator import RemoteQueueCreator
from turbo_c2.queues.simple_ebf_queue import SimpleEbfQueue
from turbo_c2.central_api.central_api_api import CentralApiApi
from turbo_c2.scheduler.remote_scheduler import RemoteScheduler
from turbo_c2.scheduler.scheduler import Scheduler
from turbo_c2.globals.scheduler_globals import SchedulerGlobals
from turbo_c2.interfaces.dynamic_job_definition import DynamicJobDefinition
from turbo_c2.interfaces.job_definition import JobDefinition


def setup(scheduler_globals_object: Type[SchedulerGlobals]):
    # FIXME: Use resource mapping, global resources and shared objects
    scheduler_globals_object.scheduler_mode_mapping: dict[str, Type[Scheduler]] = {
        "local": LocalScheduler,
        "remote": RemoteScheduler,
    }
    scheduler_globals_object.queue_creator_mapping: dict[str, Type[QueueCreator]] = {
        "local": LocalQueueCreator,
        "remote": RemoteQueueCreator,
    }
    scheduler_globals_object.queue_controller_mapping: dict[
        str, Type[QueueController]
    ] = {
        "local": LocalQueueController,
        "remote": RemoteQueueController,
    }
    scheduler_globals_object.queue_api_mapping: dict[str, Type[QueueApi]] = {
        "local": None,
        "remote": RemoteQueueApi,
    }
    scheduler_globals_object.queue_definition_mapping: dict[
        Type[QueueDefinition], Type[EBFQueue]
    ] = {
        QueueDefinition: (SimpleEbfQueue, "default"),
    }
    scheduler_globals_object.job_creator_mapping: dict[str, Type[DefaultJobCreator]] = {
        "local": LocalJobCreator,
        "remote": RemoteJobControllerCreator,
    }
    scheduler_globals_object.job_definition_mapping: dict[
        Type[JobDefinition], Type[JobWithQueueEvaluation]
    ] = {
        JobDefinition: (JobWithQueueEvaluation, None),
        DynamicJobDefinition: (DynamicJob, "default"),
    }
    scheduler_globals_object.job_controller_mapping: dict[str, Type[JobController]] = {
        "local": LocalJobController,
        "remote": RemoteJobController,
    }
    scheduler_globals_object.job_api_mapping: dict[str, Type[JobApi]] = {
        "local": None,
        "remote": RemoteJobApi,
    }
    scheduler_globals_object.queue_mapping: dict[str, Type[EBFQueue]] = {
        "remote": SimpleEbfQueue
    }
    scheduler_globals_object.central_api_mapping: dict[str, Type[DefaultCentralApi]] = {
        "remote": CentralApiApi
    }
    scheduler_globals_object.state_machine_mapping: dict[str, Any] = {
        "job_controller": {"remote": None, "local": None}
    }

    local_storage_external_api = LocalStorageExternalApi("local_storage", "./local_storage/default")
    json_local_storage_external_api = JsonLocalStorageExternalApi("json_local_storage", "./local_storage/json")
    job_extra_api = turbo_job_extra_api.JobExtraApi()
    job_extra_api.add_external_api(local_storage_external_api)

    scheduler_globals_object.global_mapping: dict[str, Any] = {}
    scheduler_globals_object.config = DefaultConfig()
    scheduler_globals_object.add_extra_api(job_extra_api)
    scheduler_globals_object.add_extra_api(queue_extra_api.QueueExtraApi())
    scheduler_globals_object.add_extra_api(GroupExtraApi())
    scheduler_globals_object.add_extra_api(ExternalApiExtraApi())
    scheduler_globals_object.add_extra_api(ClientExtraApi())

    gui_extra_api = GuiExtraApi()
    gui_extra_api.add_external_api(json_local_storage_external_api)

    scheduler_globals_object.add_extra_api(gui_extra_api)

    job_instance_creator = DefaultJobInstanceCreator()
    job_controller_creator = RemoteJobControllerCreator()

    prometheus_host = os.environ.get("PROMETHEUS_HOST", "http://localhost")

    scheduler_globals_object.set_resource_mapping(
        ["init", "needs_central_api", "job_instance_creator"],
        job_instance_creator
    )

    scheduler_globals_object.set_resource_mapping(
        ["init", "needs_central_api", "job_controller_creator"],
        job_controller_creator
    )

    scheduler_globals_object.set_resource_mapping(
        ["init", "load", "job_extra_api"],
        job_extra_api
    )

    scheduler_globals_object.set_resource_mapping(
        ["client", "prometheus", "init"],
        (ClientDefinition.set, ({"resource_id": PrometheusHttpClient, "resource": PrometheusHttpClient(prometheus_host, 9090)})),
    )

    scheduler_globals_object.set_resource_mapping(
        ["external_api", "storage_api", "init"],
        (ExternalApiDefinition.set, ({"resource_id": LocalStorageExternalApi, "resource": local_storage_external_api})),
    )

    scheduler_globals_object.set_resource_mapping(
        ["external_api", "json_storage_api", "init"],
        (ExternalApiDefinition.set, ({"resource_id": JsonLocalStorageExternalApi, "resource": json_local_storage_external_api})),
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "job_group", "init"],
        (GroupCreatorDefinition.set, ({"resource_id": JobGroup, "resource": GroupCreator()})),
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "job_definition_creator", "init"],
        (JobDefinitionCreatorDefinition.set, ({"resource_id": JobDefinition, "resource": JobDefinitionCreator()}))
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "job_instance_creator", "init"],
        (JobInstanceCreatorDefinition.set, ({"resource_id": JobInstanceData, "resource": job_instance_creator}))
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "job_controller_creator", "init"],
        (JobControllerCreatorDefinition.set, ({"resource_id": JobInstance, "resource": job_controller_creator}))
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "layout", "init"],
        (LayoutDefinitionCreatorDefinition.set, ({"resource_id": LayoutDefinition, "resource": LayoutDefinitionCreator()}))
    )

    scheduler_globals_object.set_resource_mapping(
        ["extra_api_definition", "layout_element", "init"],
        (LayoutElementCommandCreatorDefinition.set, ({"resource_id": LayoutElementCommand, "resource": LayoutElementCommandCreator()}))
    )
