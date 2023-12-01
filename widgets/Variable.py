import asyncio
import inspect
from typing import Any
import tkinter


SETTING = {
    "startup": False,
    "run-on-background": True,
    "refresh-time": 10,
    "craft-shortcut": False,
    "allows-start-menu": False,
    "allows-desktop": False,
    "overwrite-setting": True,
    "backup-setting": False,
    "language": "eng",
    "version": "1.0.2"
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

class Setting(BaseVariable):
    def __init__(self, root = None) -> None:
        super().__init__()
        self.raw_setting: dict = SETTING
        self.data = {}
        
        for key, value in self.raw_setting.items():
            if isinstance(value, bool):
                value = tkinter.BooleanVar(root, value)
            elif isinstance(value, int):
                value = tkinter.IntVar(root, value)
            elif isinstance(value, float):
                value = tkinter.DoubleVar(root, value)
            elif isinstance(value, str):
                value = tkinter.StringVar(root, value)
                
        
            self.data[key] = value
            
                
        
    def __getitem__(self, key) -> tkinter.Variable:
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key].set(value)
        self._callback_call()

    def set(self, key, value):
        self.data[key].set(value)
        self._callback_call()

    def from_dict(self, value: Any):
        
        for key, value_ in value.items():
            self.data[key].set(value_)

        self._callback_call()

    def get(self):
        for key, value in self.data.items():
            self.raw_setting[key] = value.get()
            
        return self.raw_setting
