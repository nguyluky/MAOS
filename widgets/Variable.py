import asyncio
import inspect


class ListVariable(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.callbacks = []

    def add_callback(self, callback):
        if inspect.iscoroutinefunction(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError('callback muse be async func')

    def _callback_call(self, mode: str, value: object):
        loop = asyncio.get_event_loop()
        for i in self.callbacks:
            func = i(mode, value)
            loop.create_task(func)

    def append(self, __object):
        super().append(__object)

        self._callback_call("append", __object)

    def remove(self, __value):
        super().append(__value)

        self._callback_call("remove", __value)


class CustomVariable:
    def __init__(self, value: object = None):
        self.value = value
        self.callbacks = []

    def add_callback(self, callback):
        if inspect.iscoroutinefunction(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError('callback muse be async func')

    def _callback_call(self, mode: str, value: object):
        loop = asyncio.get_event_loop()
        for i in self.callbacks:
            func = i(mode, value)
            loop.create_task(func)

    def set(self, value):
        if inspect.isfunction(value):
            self.value = value(self.value)
        else:
            self.value = value

        self._callback_call("set", value)

    def get(self):
        return self.value

