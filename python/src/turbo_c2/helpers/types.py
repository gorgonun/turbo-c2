# JSON representation in Python
from typing import Any, Hashable, Union


PJSON = dict[Hashable, Union["PJSON", dict[Hashable, Any]]] | list[Union["PJSON", Any]]
