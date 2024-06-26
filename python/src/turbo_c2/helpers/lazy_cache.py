from asyncio import Future
from typing import Callable, Generic, Hashable, TypeVar


T = TypeVar("T", bound=Hashable)
U = TypeVar("U")


class LazyCache(Generic[T, U]):
    def __init__(self, items: list[U] | None = None, key: T | None = None, get_key: Callable[[U], T] | None = None, from_dict: dict[T, U] | None = None) -> None:
        if key is not None and get_key is not None:
            raise RuntimeError("Cannot specify both key and get_key")
        
        if key is None and get_key is None:
            raise RuntimeError("Must specify either key or get_key")

        self.__items = items or []
        self.__cache: dict[Hashable, T] = {} if from_dict is None else from_dict
        self.__get_key = get_key
        self.__key = key

    @property
    def cache(self):
        return self.get_cache()
    
    def get_cache(self):
        return self.__cache
    
    def add_item(self, item: U):
        self.__items.append(item)

    def add_items(self, items: list[U]):
        self.__items += items

    def get(self, key: T, default: U | None = None) -> U | None:
        if key in self.__cache:
            return self.__cache[key]

        for item in self.__items:
            if self.__get_key:
                if self.__get_key(item) == key:
                    self.__cache[key] = item
                    return item
            else:
                if self.__key == key:
                    self.__cache[key] = item
                    return item

        return default
    
    def __getitem__(self, key: T) -> U:
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result


class AsyncLazyCache(Generic[T, U]):
    def __init__(self, items: list[U] | None = None, key: T | None = None, get_key: Callable[[U], T] | None = None, from_dict: dict[T, U] | None = None) -> None:
        if key is not None and get_key is not None:
            raise RuntimeError("Cannot specify both key and get_key")
        
        if key is None and get_key is None and from_dict is None:
            raise RuntimeError("Must specify either key or get_key")

        self.__items = items or []
        self.__get_key = get_key
        self.__cache: dict[T, U] = {} if from_dict is None else from_dict
        self.__key = key

    @property
    def cache(self):
        return self.get_cache()
    
    def get_cache(self):
        return self.__cache
    
    def add_item(self, item: U):
        self.__items.append(item)

    def add_items(self, items: list[U]):
        self.__items += items
    
    async def get(self, key: T) -> U | None:
        if key in self.__cache:
            return self.__cache[key]

        for item in self.__items:
            if self.__get_key:
                if await self.__get_key(item) == key:
                    self.__cache[key] = item
                    return item
            else:
                if self.__key == key:
                    self.__cache[key] = item
                    return item

        return None
