import ray
from turbo_c2.turbo_events.event_store.event_controller import EventController
from turbo_c2.turbo_events.events.event_reference import EventReference


class RemoteEventController(EventController):
    def __init__(self, event_store_actor_name: str):
        self.__actor_name = event_store_actor_name
        self.__actor = None

    @property
    def actor(self):
        if not self.__actor:
            self.__actor = ray.get_actor(self.__actor_name)
        return self.__actor

    def event_happened(self, event_reference: EventReference) -> bool:
        return ray.get(self.actor.event_happened.remote(event_reference))
