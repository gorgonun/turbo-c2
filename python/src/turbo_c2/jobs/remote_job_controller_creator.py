from typing import Any

import ray
from turbo_c2.extra_api.command.job.job_controller_definition import JobControllerDefinition
from turbo_c2.interfaces.job_controller_creator import JobControllerCreator
from turbo_c2.jobs.job_instance import JobInstance


class RemoteJobControllerCreator(JobControllerCreator):
    async def get_job_controller(self, job_controller_id: str | None = None):
        if not job_controller_id:
            controllers = await self.central_api.execute(JobControllerDefinition.get())
            return controllers[0]
        return await self.central_api.execute(
            JobControllerDefinition.get(job_controller_id)
        )

    async def create(
        self,
        definition: JobInstance,
        meta: dict[str, Any] | None = None,
    ):
        job_controller = await self.get_job_controller(meta.get("job_controller_id"))

        prometheus_client_actor_definition = await self.central_api.get_object_reference(["resource_creator", "actor", "metrics", "client", "prometheus"])

        if not prometheus_client_actor_definition:
            raise RuntimeError("Prometheus client actor not found")

        metrics_client = prometheus_client_actor_definition.actor_ref

        actor_ref = ray.remote(job_controller).options(num_cpus=0.1, memory=250 * 1024 * 1024, name=definition.instance_resource_id).remote(
                definition, metrics_client
            )
        
        # Blocking until actor finishes creation and returns the reference.
        # It take some time for it to finish creation and I couldn't find a way to wait until it's done.
        await actor_ref.get_definition.remote()

        return actor_ref
