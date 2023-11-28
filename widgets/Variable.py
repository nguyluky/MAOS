import asyncio
import inspect
from typing import Any


SETTING = {
    "startup": {
        "displayName": "startup with window",
        "type": 0,
        "value_": False,
        "description": None
    },
    "run-on-background": {
        "displayName": "run on background",
        "type": 0,
        "value_": False,
        "description": "keep launcher run when your in game"
    },
    "refresh-time": {
        "displayName": "refresh time",
        "type": 1,
        "value_": 10,
        "description": None
    },
    "craft-shortcut": {
        "displayName": "Quick access",
        "type": 0,
        "value_": False,
        "description": "create shortcut of each account"
    },
    "allows-start-menu": {
        "displayName": "Allows start menu",
        "type": 0,
        "value_": False,
        "description": "Allows create shortcut to start menu",
        
    },
    "overwrite-setting": {
        "displayName": "overwrite setting",
        "type": 0,
        "value_": False,
        "description": "overwrite your setting in game"
    }
}


class BaseVariable:
    def __init__(self) -> None:
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def _callback_call(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        for i in self.callbacks:
            func = i(*args, **kwargs)
            if inspect.iscoroutinefunction(i):
                loop.create_task(func)


class ListVariable(list, BaseVariable):
    def __init__(self, *args):
        super(list, self).__init__(*args)
        super(ListVariable, self).__init__()

    def append(self, __object):
        super().append(__object)

        self._callback_call("append", __object)

    def remove(self, __value):
        super().append(__value)

        self._callback_call("remove", __value)


class CustomVariable(BaseVariable):
    def __init__(self, value: object = None):
        super().__init__()
        self.value = value

    def set(self, value):
        if inspect.isfunction(value):
            self.value = value(self.value)
        else:
            self.value = value

        self._callback_call("set", value)

    def get(self):
        return self.value


# TODO hoàn thành setting class
class Setting(BaseVariable):
    def __init__(self) -> None:
        super().__init__()
        self.data: dict = SETTING

    def __getitem__(self, key):
        return self.data[key]['value_']

    def __setitem__(self, key, value):
        self.data[key] = value
        self._callback_call()

    def set(self, key, value):
        self.data[key]['value_'] = value
        self._callback_call()

    def from_dict(self, value: Any):
        for key, value_ in value.items():
            self.data[key] = value_

        self._callback_call()

    def get(self):
        return self.data
