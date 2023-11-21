from customtkinter import *

from ValLib import EndPoints
from widgets.Structs import TabViewFrame


class Match(CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)


class MatchHistory(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # setup value
        self.match_history = {

        }

        # render layout
        self.main_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)

    def show(self):
        super().show()
