from turbo_c2.central_queue_event_manager import CentralQueueEventManager


class HasCentralQueueEventManager():
    def __init__(self, central_queue_event_manager: CentralQueueEventManager) -> None:
        self.__central_queue_event_manager = central_queue_event_manager

    @property
    def central_queue_event_manager(self):
        return self.__central_queue_event_manager
