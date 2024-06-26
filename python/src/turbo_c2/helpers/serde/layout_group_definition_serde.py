from turbo_c2.domain.gui.layout_definition import LayoutGroupDefinition
from turbo_c2.helpers.serde.pydantic_serde import DefaultPydanticSerDe


class LayoutGroupDefinitionSerDe(DefaultPydanticSerDe[LayoutGroupDefinition]):
    element_type = LayoutGroupDefinition
