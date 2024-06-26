from typing import Any, Callable


def get_annotated_kwargs(mapping: dict[str, Any], function: Callable[..., Any]) -> dict[str, Any]:
    return {key: mapping[key] for key in function.__code__.co_varnames if key in mapping}
