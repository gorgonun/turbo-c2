from turbo_c2.domain.gui.layout_definition import LayoutDefinition
from turbo_c2.helpers.serde.pydantic_serde import DefaultPydanticSerDe


class LayoutDefinitionSerDe(DefaultPydanticSerDe[LayoutDefinition]):
    element_type = LayoutDefinition
