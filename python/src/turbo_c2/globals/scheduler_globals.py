from dataclasses import dataclass
from typing import Any, Hashable, Tuple, Type

from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.central_api.default_central_api import DefaultCentralApi
from turbo_c2.config.config import Config
from turbo_c2.extra_api.default_extra_api import DefaultExtraApi
from turbo_c2.helpers.path_mapping import PathMapping
from turbo_c2.interfaces.central_api import CentralApi
from turbo_c2.interfaces.job_api import JobApi
from turbo_c2.interfaces.job_controller import JobController
from turbo_c2.interfaces.queue_api import QueueApi
from turbo_c2.jobs.default_job_creator import DefaultJobCreator
from turbo_c2.jobs.job_definition_with_settings import JobDefinitionWithSettings
from turbo_c2.jobs.job_instance import JobInstance
from turbo_c2.jobs.job_with_queue_evaluation import JobWithQueueEvaluation
from turbo_c2.mixin.needs_queue_evaluation import NeedsQueueEvaluation
from turbo_c2.queues.ebf_queue import EBFQueue
from turbo_c2.queues.queue_controller import QueueController
from turbo_c2.queues.queue_creator import QueueCreator
from turbo_c2.queues.queue_definition import QueueDefinition
from turbo_c2.scheduler.scheduler import Scheduler
from turbo_c2.interfaces.job_definition import JobDefinition


@dataclass
class SchedulerDefinitions:
    jobs: list[JobDefinitionWithSettings]
    apis: list[DefaultExtraApi]


class SchedulerGlobals:
    __scheduler_jobs: list[JobDefinitionWithSettings] = []
    __job_groups_mapping: PathMapping = PathMapping()
    __scheduler_queues: list[QueueDefinition] = []
    __scheduler_apis: list[DefaultExtraApi] = []
    __remote_mapping: dict[str, Any] = {}
    __remote_only: bool = False
    __shared_objects: dict[str, Any] = {}
    __needs_queue_evaluations: list[NeedsQueueEvaluation] = []
    __local_resources = PathMapping()
    __resources_mapping = PathMapping()
    __central_api: CentralApi | None = None
    scheduler_mode_mapping: dict[str, Type[Scheduler]] = {}
    queue_creator_mapping: dict[str, Type[QueueCreator]] = {}
    queue_controller_mapping: dict[str, Type[QueueController]] = {}
    queue_api_mapping: dict[str, Type[QueueApi]] = {}
    queue_definition_mapping: dict[Type[QueueDefinition], Tuple[Type[EBFQueue], str | None]] = {}
    job_creator_mapping: dict[str, Type[DefaultJobCreator]] = {}
    job_definition_mapping: dict[Type[JobDefinition], Tuple[Type[JobWithQueueEvaluation], str | None]] = {}
    job_controller_mapping: dict[str, Type[JobController]] = {}
    job_api_mapping: dict[str, Type[JobApi]] = {}
    queue_mapping: dict[str, Type[EBFQueue]] = {}
    central_api_mapping: dict[str, Type[DefaultCentralApi]] = {}
    state_machine_mapping: dict[str, Any] = {}
    global_mapping: dict[str, Any] = {}
    config: Config
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_central_api(cls):
        return cls.__central_api

    @classmethod
    def set_central_api(cls, central_api: CentralApi):
        cls.__central_api = central_api
    
    @classmethod
    def get_resource_mappings(cls, prefix: str | None = None, suffix: str | None = None, matches: str | None = None):
        return cls.__resources_mapping.get_all_resources(prefix=prefix, suffix=suffix, matches=matches)
    
    @classmethod
    def set_resource_mapping(cls, path: list[Hashable], resource: Any):
        cls.__resources_mapping.put_resource(path, resource)

    @classmethod
    def get_resource_mapping(cls, path: list[Hashable]):
        return cls.__resources_mapping.get_resource(path)

    @classmethod
    def get_job_for_definition(cls, job_definition: JobDefinition):
        return cls.job_definition_mapping[type(job_definition)]
    
    @classmethod
    def get_job_definition_mapping(cls):
        return cls.job_definition_mapping

    @classmethod
    def is_remote_only(cls):
        return cls.__remote_only

    @classmethod
    def setup(cls, scheduler_definitions: SchedulerDefinitions):
        cls.__scheduler_jobs += scheduler_definitions.jobs
        cls.__scheduler_queues += scheduler_definitions.queues
        return cls
    
    @classmethod
    def queue_controller(cls) -> Type[QueueController]:
        return cls.queue_controller_mapping[cls.config.mode]
    
    @classmethod
    def job_controller(cls) -> Type[JobController]:
        return cls.job_controller_mapping[cls.config.mode]
    
    @classmethod
    def queue_api(cls) -> Type[QueueApi]:
        return cls.queue_api_mapping[cls.config.mode]
    
    @classmethod
    def job_api(cls) -> Type[JobApi]:
        return cls.job_api_mapping[cls.config.mode]

    @classmethod
    def default_job_creator(cls):
        return cls.job_creator_mapping[cls.config.mode]

    @classmethod
    def default_queue_creator(cls):
        return cls.queue_creator_mapping[cls.config.mode]

    @classmethod
    def default_queue(cls):
        return cls.queue_mapping[cls.config.mode]
    
    @classmethod
    def queue_type_mapping(cls):
        return cls.queue_definition_mapping

    @classmethod
    def default_central_api(cls):
        central_api = cls.central_api_mapping[cls.config.mode](
            cls.config.central_api_identifier
        )
        return central_api

    @classmethod
    def get_transition_function(self, identificator: str, state: str):
        return self.state_machine_mapping[identificator][state]
    
    @classmethod
    def create_job_group(cls, name: str, path: str, meta: dict[str, Any], fail_if_exists: bool = False, description: str | None = None):
        job_group: JobGroupWithInstances = cls.__job_groups_mapping.get_resource(path.split("/"))

        if job_group:
            if fail_if_exists:
                raise RuntimeError(f"Job group {name} already exists.")
            
            job_group.meta.update(meta)
            return job_group

        job_group = JobGroupWithInstances(
            name=name,
            path=path,
            meta=meta,
            description=description
        )

        cls.__job_groups_mapping.put_resource(path.split("/"), job_group)
        return job_group
    
    @classmethod
    def add_job_instance_to_group(cls, job_instance: JobInstance, group_path: str | None = None):
        job_group: JobGroupWithInstances = cls.__job_groups_mapping.get_resource((group_path or "").split("/"))
        if not job_group:
            raise ValueError(f"Job group {group_path} does not exist.")

        job_group.job_instances.append(job_instance)
        cls.__job_groups_mapping.put_resource((group_path or "").split("/"), job_group)

    @classmethod
    def get_job_groups(cls) -> list[Tuple[list[str], JobGroupWithInstances]]:
        return cls.__job_groups_mapping.get_all_resources()

    @classmethod
    def add_job(
        cls,
        job_definition: JobDefinition,
    ):
        cls.__scheduler_jobs.append(
            job_definition
        )

    @classmethod
    def add_jobs(
        cls,
        jobs_definitions: list[JobDefinition],
    ):

        cls.__scheduler_jobs.extend(jobs_definitions)

    @classmethod
    def get_jobs(cls):
        return cls.__scheduler_jobs

    @classmethod
    def add_queue(cls, queue: QueueDefinition):
        if cls.__remote_only:
            return cls._add_remote("queue", queue)

        cls.__scheduler_queues.append(queue)

    @classmethod
    def add_queues(cls, queues: list[QueueDefinition]):
        if cls.__remote_only:
            return cls._add_remote("queue", *queues)

        cls.__scheduler_queues.extend(queues)

    @classmethod
    def get_queues(cls):
        return cls.__scheduler_queues

    @classmethod
    def set_remote_mapping(cls, mapping: dict[str, Any]):
        cls.__remote_mapping = mapping

    @classmethod
    def set_remote_only(cls, remote_only: bool):
        cls.__remote_only = remote_only

    @classmethod
    def add_needs_queue_evaluation(cls, needs_queue_evaluation: NeedsQueueEvaluation):
        cls.__needs_queue_evaluations.append(needs_queue_evaluation)

    @classmethod
    def get_needs_queue_evaluations(cls):
        return cls.__needs_queue_evaluations

    @classmethod
    def _add_remote(cls, name: str, *objs: Any):
        raise NotImplementedError()
        # if not cls.__remote_mapping[name]:
        #     raise Exception(f"No remote mapping for {name} found.")

        # for obj in objs:
        #     ray.get(cls.__remote_mapping[name].put.remote(obj))

    @classmethod
    def get_shared_object(cls, name: str):
        return cls.__shared_objects.get(name)

    @classmethod
    def set_shared_object(cls, name: str, obj: Any):
        cls.__shared_objects[name] = obj

    @classmethod
    def add_extra_api(cls, api: DefaultExtraApi):
        cls.__scheduler_apis.append(api)

    @classmethod
    def get_extra_apis(cls):
        return cls.__scheduler_apis
