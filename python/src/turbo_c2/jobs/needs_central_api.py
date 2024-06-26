from turbo_c2.interfaces.central_api import CentralApi


class NeedsCentralApi:
    def __init__(self, central_api: CentralApi | None = None):
        self.__central_api: CentralApi | None = central_api

    @property
    def central_api(self):
        return self.__central_api
    
    def get_central_api(self) -> CentralApi | None:
        return self.__central_api
    
    def add_central_api(self, central_api: CentralApi):
        self.__central_api = central_api
