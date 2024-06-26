from itertools import chain
from typing import Any, Callable, Hashable, Union


RecursiveData = dict[Hashable, Union["RecursiveData", dict[Hashable, Any]]]


class NotFoundElement:
    pass


def traverse_data(
    data: RecursiveData, datum: list[tuple[str, Hashable]], raise_if_not_found=False
) -> Any:
    pointers: list[tuple[Hashable, RecursiveData]] = []

    if not data:
        return

    cursor = data

    pointers.append((cursor, None))

    for key, value in datum:
        cursor = cursor.get(key, NotFoundElement)
        if cursor == NotFoundElement:
            if raise_if_not_found:
                raise KeyError(f"Key {key} not found on data")
            return

        pointers.append((cursor, key))

        cursor = cursor.get(value, NotFoundElement)
        if cursor == NotFoundElement:
            if raise_if_not_found:
                raise KeyError(f"Value {value} not found on data")
            return

        pointers.append((cursor, value))

    return cursor, pointers


def delete_resource_from_path(
    mapping: RecursiveData, path: list[tuple[str, Hashable]], resource_key: Hashable, fail_if_not_found=True
):
    result = traverse_data(mapping, path, True)

    if result is None:
        if fail_if_not_found:
            raise KeyError(f"Resource not found on path {path}")
        return
    
    cursor, pointers = result

    if isinstance(cursor, dict):
        del cursor[resource_key]

    if len(cursor) == 0:
        delete_empty_keys(pointers)


def delete_empty_keys(pointers: list[RecursiveData]):
    for i in range(len(pointers) - 1, -1, -1):
        pointer, key = pointers[i]
        if len(pointer) == 0:
            if i == 0:
                break

            del pointers[i - 1][0][key]

        else:
            break


def get_all_matching_elements(
    mapping: RecursiveData,
    keys: list[tuple[str, Any]],
    skip_last_generic=False,
    generic_element=None,
):
    """
    Gets all matching elements from a mapping using a list of keys.
    skip_last_generic: If True, the last key will not be considered as a generic element. Can be used when keys are not final.
    generic_element: The element which will be used as wildcard.
    """

    if not keys:
        return []

    def __get_all_matching_elements(
        mapping: dict, index: int, path: list[Hashable] = []
    ) -> list[tuple[list[Hashable], Any]]:
        def get_last_element_by_key():
            if keys[index][1] != generic_element:
                return [
                        (
                            [*path, (keys[index][0], keys[index][1])],
                            cursor.get(keys[index][1], {}),
                        ),
                    ]
            
            return [
                (
                    [*path, (keys[index][0], key)],
                    cursor.get(key, {}),
                )
                for key in cursor.keys()
            ]

        if not keys:
            return {}

        cursor = mapping.get(keys[index][0], NotFoundElement)

        if cursor == NotFoundElement:
            return [([], None)]

        if index == len(keys) - 1:
            if skip_last_generic:
                return get_last_element_by_key()

            return [
                *get_last_element_by_key(),
                (
                    [*path, (keys[index][0], generic_element)],
                    cursor.get(generic_element, {}),
                ),
            ]

        if keys[index][1] != generic_element:
            result_by_generic: list[tuple[list[Hashable], Any]] = list(
                filter(
                    lambda x: x[1] is not None,
                    __get_all_matching_elements(
                        cursor.get(generic_element, {}),
                        index + 1,
                        [*path, (keys[index][0], generic_element)],
                    ),
                )
            )

            result_by_key: list[tuple[list[Hashable], Any]] = list(
                filter(
                    lambda x: x[1] is not None,
                    __get_all_matching_elements(
                        cursor.get(keys[index][1], {}),
                        index + 1,
                        [*path, (keys[index][0], keys[index][1])],
                    ),
                )
            )
            return [*result_by_key, *result_by_generic]

        else:
            keys_to_search = list(cursor.keys())

            result = list(
                filter(
                    lambda x: x[1],
                    chain.from_iterable([
                        __get_all_matching_elements(
                            cursor[key], index + 1, [*path, (keys[index][0], key)]
                        )
                        for key in keys_to_search
                    ]),
                )
            )

            return result

    return __get_all_matching_elements(mapping, 0)


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
