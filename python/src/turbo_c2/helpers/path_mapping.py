import functools
import re
from typing import Any, Hashable, Tuple, Type

from turbo_c2.helpers.cursor_utils import delete_resource_from_path
from turbo_c2.helpers.turbo_logger import TurboLogger


class PathMapping:
    def __init__(self, mapping: dict[str, Any] | None = None) -> None:
        self.__mapping = mapping or {}
        self.__resource_key = "__path_mapping__resource__"
        self.__logger = TurboLogger("PathMapping")

    @property
    def mapping(self):
        return self.__mapping

    def get_resource(self, obj_ids: list[Hashable]):
        cursor = self.__mapping

        for obj_id in obj_ids:
            cursor = cursor.get(obj_id)
            if not cursor:
                return None

        if self.__resource_key not in cursor:
            return cursor

        return cursor.get(self.__resource_key)

    def put_resource(self, obj_ids: list[Hashable], resource: Any):
        cursor = self.__mapping

        for obj_id in obj_ids:
            cursor = cursor.setdefault(obj_id, {})

        cursor[self.__resource_key] = resource

    def get_all_paths(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None):
        self.__logger.debug("GET ALL PATHS", prefix, suffix, matches)
        re_matches = re.compile(matches) if matches else None

        def get_paths(cursor, path: list[str]) -> list[str]:
            if isinstance(cursor, dict):
                return [
                    paths
                    for key in cursor.keys()
                    for paths in get_paths(cursor[key], [*path, key])
                ]

            path.pop()
            str_path = "/".join(map(self.serialize_type, path))
            if re_matches and not re_matches.match(str_path):
                return []
            
            if suffix and not str_path.endswith(suffix):
                return []

            return [path]

        root = prefix.split("/") if prefix else []
        cursor = self.move_cursor(self.__mapping, root)

        return get_paths(cursor, root)

    def get_all_resources(self, prefix: str | None = None, suffix: str | None = None, matches: str | None = None):
        self.__logger.debug("GET ALL RESOURCES", prefix, suffix, matches)
        re_matches = re.compile(matches) if matches else None

        def get_paths(cursor, path: list[str], is_self_key: bool) -> list[Tuple[list[str], Any]]:
            if isinstance(cursor, dict) and not is_self_key:
                return [
                    path_with_resource
                    for key in cursor.keys()
                    for path_with_resource in get_paths(cursor[key], [*path, key], key == self.__resource_key)
                ]

            path.pop()
            str_path = "/".join(map(self.serialize_type, path))
            if re_matches and not re_matches.match(str_path):
                return []
            
            if suffix and not str_path.endswith(suffix):
                return []

            return [(path, cursor)]

        root = prefix.split("/") if prefix else []

        try:
            cursor = self.move_cursor(self.__mapping, root)

        except KeyError:
            return []

        return get_paths(cursor, root, False)

    def move_cursor(self, cursor, positions: list[str]):
        for position in positions:
            cursor = cursor[position]

        return cursor
    
    def serialize_type(self, t: Any | Type[Any]):
        return t if not isinstance(t, type) else f"type(${type(t)})"
    
    def delete_item(self, path: list[str]):
        return delete_resource_from_path(self.__mapping, path, self.__resource_key)
    
    def delete_keys(self, keys: list[str]):
        if len(keys) == 0:
            self.__mapping = {}
            return

        return delete_resource_from_path(self.__mapping, keys[:-1], keys[-1])
    
    def __reduce__(self) -> str | Tuple[Any]:
        return functools.partial(
            PathMapping,
            self.__mapping,
        ), tuple()
