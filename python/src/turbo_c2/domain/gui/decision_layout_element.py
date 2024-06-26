from dataclasses import dataclass


@dataclass
class DecisionLayoutElement:
    x: float | None = None
    y: float | None = None
    width: int | None = None
    height: int | None = None
    resource_name: str | None = None
    edges: list[tuple[str, str]] | None = None
