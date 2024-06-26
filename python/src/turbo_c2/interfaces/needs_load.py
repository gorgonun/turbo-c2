import abc


class NeedsLoad(abc.ABC):
    def __init__(self):
        self._is_loaded = False

    @property
    def is_loaded(self):
        return self._is_loaded
    
    @abc.abstractmethod
    async def on_load(self):
        pass

    async def load(self):
        await self.on_load()
        self._is_loaded = True

    async def on_unload(self):
        pass

    async def unload(self):
        await self.on_unload()
        self._is_loaded = False
