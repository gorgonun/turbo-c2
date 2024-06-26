import asyncio


class LockProvider:
    @classmethod
    def get_lock(cls):
        return asyncio.Lock()
