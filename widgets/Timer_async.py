import asyncio


# scr https://stackoverflow.com/questions/45419723/python-timer-with-asyncio-coroutine/45430833#45430833
class SetInterval:
    def __init__(self, timeout, callback, *args):
        self._timeout = timeout
        self._callback = callback
        self._task = None

    def star(self):
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        while True:
            await self._callback()
            await asyncio.sleep(self._timeout)

    def cancel(self):
        if self._task is not None:
            self._task.cancel()


class SetTimeout:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()
