import asyncio
import inspect
from typing import Any
import tkinter
from tkinter import BooleanVar, IntVar, DoubleVar, StringVar
from dataclasses import dataclass
SETTING = {
    "startup": False,
    "run_on_background": True,
    "refresh_time": 10,
    "craft_shortcut": False,
    "allows_start_menu": False,
    "allows_desktop": False,
    "overwrite_setting": True,
    "backup_setting": False,
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


class Setting:
    startup: BooleanVar = None
    run_on_background: BooleanVar = None
    refresh_time: IntVar = None
    craft_shortcut: BooleanVar = None
    allows_start_menu: BooleanVar = None
    allows_desktop: BooleanVar = None
    overwrite_setting: BooleanVar = None
    backup_setting: BooleanVar = None
    language: StringVar = None
    version: StringVar = None
    
    def __init__(self, root=None) -> None:
        super().__init__()
        self.startup = BooleanVar(root, False)
        self.run_on_background = BooleanVar(root, False)
        self.refresh_time = IntVar(root, 10)
        self.craft_shortcut = BooleanVar(root, True)
        self.allows_start_menu = BooleanVar(root, False)
        self.allows_desktop = BooleanVar(root, False)
        self.overwrite_setting = BooleanVar(root, True)
        self.backup_setting = BooleanVar(root, False)
        self.language = StringVar(root, "en")
        self.version = StringVar(root, "1.0.1")
        self.default_account = StringVar(root, "")

    def from_dict(self, dict_: dict) -> None:
        self.startup.set(dict_.get("startup", self.startup.get()))
        self.run_on_background.set(dict_.get("run_on_background", self.run_on_background.get()))
        self.refresh_time.set(dict_.get("refresh_time", self.refresh_time.get()))
        self.craft_shortcut.set(dict_.get("craft_shortcut", self.craft_shortcut.get()))
        self.allows_start_menu.set(dict_.get("allows_start_menu", self.allows_start_menu.get()))
        self.allows_desktop.set(dict_.get("allows_desktop", self.allows_desktop.get()))
        self.overwrite_setting.set(dict_.get("overwrite_setting", self.overwrite_setting.get()))
        self.backup_setting.set(dict_.get("backup_setting", self.backup_setting.get()))
        self.language.set(dict_.get("language", self.language.get()))
        self.version.set(dict_.get("version", self.version.get()))
        self.default_account.set(dict_.get("default_account", self.default_account.get()))

    def to_dict(self) -> dict:
        return {
            "startup": self.startup.get(),
            "run_on_background": self.run_on_background.get(),
            "refresh_time": self.refresh_time.get(),
            "craft_shortcut": self.craft_shortcut.get(),
            "allows_start_menu": self.allows_start_menu.get(),
            "allows_desktop": self.allows_desktop.get(),
            "overwrite_setting": self.overwrite_setting.get(),
            "backup_setting": self.backup_setting.get(),
            "language": self.language.get(),
            "version": self.version.get(),
            "default_account": self.default_account.get()
        }