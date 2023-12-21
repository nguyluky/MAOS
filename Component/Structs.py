import inspect
import asyncio

from customtkinter import *


class TabViewFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_show = False

    def show(self):
        self.pack(fill=BOTH, expand=True)
        self.is_show = True

    def hidden(self):
        self.pack_forget()
        self.is_show = False


class BaseMainFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(fg_color="#202020", *args, **kwargs)

        self.callbacks = []
        self.loop = asyncio.get_event_loop()
        self.is_show = False

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callback(self):
        for func in self.callbacks:
            tem = func()
            if inspect.iscoroutinefunction(func):
                self.loop.create_task(tem)

    def show(self):
        self.pack(fill=BOTH, expand=True)
        self.is_show = True

    def hidden(self):
        self.pack_forget()
        self.is_show = False
