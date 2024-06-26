from typing import Any, Callable, Hashable, Union


RecursiveData = dict[Hashable, Union["RecursiveData", dict[Hashable, Any]]]


class NotFoundElement:
    pass


def traverse_data(
    data: RecursiveData, datum: list[str, Hashable], raise_if_not_found=False
) -> tuple[Any, list[tuple[RecursiveData, Hashable]]] | None:
    pointers: list[tuple[RecursiveData, Hashable]] = []

    if not data:
        return

    cursor = data

    pointers.append((cursor, None))

    for key in datum:
        cursor = cursor.get(key, NotFoundElement)
        if cursor == NotFoundElement:
            if raise_if_not_found:
                raise KeyError(f"Key {key} not found on data")
            return

        pointers.append((cursor, key))

    return cursor, pointers


def delete_resource_from_path(
    mapping: RecursiveData, path: list[Hashable], resource_key: Hashable, fail_if_not_found=True
):
    result = traverse_data(mapping, path, True)

    if result is None:
        if fail_if_not_found:
            raise KeyError(f"Resource not found on path {path}")
        return []
    
    cursor, pointers = result

    if isinstance(cursor, dict):
        del cursor[resource_key]

    if len(cursor) == 0:
        return delete_empty_keys(pointers)
    
    return []


def delete_empty_keys(pointers: list[tuple[RecursiveData, Hashable]]):
    deleted_keys: list[Hashable] = []

    for i in range(len(pointers) - 1, -1, -1):
        pointer, key = pointers[i]
        if len(pointer) == 0:
            if i == 0:
                break

            del pointers[i - 1][0][key]
            deleted_keys.append(key)

        else:
            break

    return deleted_keys


def get_all_elements(
    mapping: RecursiveData,
    key_names: list[str],
    skip_values: set[Hashable] = None,
    get_values: Callable[[Hashable, Hashable], Hashable] = None,
):
    """
    Gets all elements from a mapping using a list of keys.
    mapping: The mapping that will be used to get the elements. The final element (after key, value of last key_name) must be a dict.
    key_names: A list of key names that will be used to get the elements.
    skip_values: A set of values that will be skipped.
    get_values: A function that will be used to get the values from the keys after skip_values filter. It will be deduplicated later by hash.
    """

    skip_values = skip_values or set()
    get_values = get_values or (lambda key, value: value)

    if not key_names:
        return {}

    def __get_all_elements(mapping: dict, index: int):
        cursor = mapping.get(key_names[index], NotFoundElement)
        if cursor == NotFoundElement:
            return {}

        if not isinstance(cursor, dict):
            raise ValueError(f"Expected a dict, but got {type(cursor)}")

        values = {
            get_values(key_names[index], x)
            for x in cursor.keys()
            if x not in skip_values
        }

        if len(values) == 0:
            raise ValueError(f"Expected values from key {key_names[index]}")

        if index == len(key_names) - 1:
            return {
                final_dict_key: final_dict_value
                for value in values
                for final_dict_key, final_dict_value in cursor[value].items()
            }

        return {
            key: value
            for d in [__get_all_elements(cursor[value], index + 1) for value in values]
            for key, value in d.items()
        }

    return __get_all_elements(mapping, 0)


def put_resource(mapping: dict, obj_ids: list[Hashable], resource: Any):
    cursor = mapping

    for obj_id in obj_ids[:-1]:
        cursor = cursor.setdefault(obj_id, {})

    cursor[obj_ids[-1]] = resource
