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
