from turbo_c2.interfaces.external_api import ExternalApi


class NeedsExternalApis:
    def __init__(self, external_apis_names: list[str], external_apis: dict[str, ExternalApi] | None = None):
        self.__external_apis_names: list[str] = external_apis_names
        self.__external_apis: dict[str, ExternalApi | None] = external_apis or {}

    @property
    def external_apis(self):
        return self.__external_apis
    
    @property
    def external_apis_names(self):
        return self.__external_apis_names
    
    def get_external_api(self, name: str) -> ExternalApi | None:
        return self.__external_apis.get(name)
    
    def add_external_api(self, name: str, external_api: ExternalApi):
        if name in self.__external_apis_names:
            self.__external_apis[name] = external_api

        else:
            raise ValueError(f"External API {name} is not allowed for this job")

    def set_external_apis_from_mapping(self, external_apis: dict[str, ExternalApi]):
        for name, external_api in external_apis.items():
            self.add_external_api(name, external_api)
