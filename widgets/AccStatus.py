from typing import Union, Tuple

from customtkinter import *

OFFLINE: str = 'off'
ONLINE: str = 'on'


class AccStatus(CTkFrame):
    def __init__(self, master, status: Union[str, Tuple[int, int]], *arg, **kw):
        super().__init__(master, fg_color="transparent", *arg, **kw)

        self.font_status = CTkFont('Consolas', 30, "bold")

        self.set_status(status)

    def _in_math_wiget(self, status):

        # hiển thị kết quả trận đấu
        label1 = CTkLabel(self, text=status[0], font=self.font_status, text_color="#20FECA", anchor="e")
        label2 = CTkLabel(self, text="-", font=self.font_status)
        label3 = CTkLabel(self, text=status[1], font=self.font_status, text_color="#FF4557", anchor='w')

        label1.pack(side=LEFT, expand=True, fill='x')
        label2.pack(side=LEFT, padx=10)
        label3.pack(side=LEFT, expand=True, fill='x')

    def _online_wiget(self):
        status = CTkLabel(self, text="ONLINE", font=self.font_status, text_color="#20FECA")
        status.pack(expand=True, fill='both')

    def _in_match_wiget(self):
        status = CTkLabel(self, text="IN-MATCH", font=self.font_status, text_color="#20FECA")
        status.pack(expand=True, fill='both')

    def _offline_wiget(self):
        status = CTkLabel(self, text="OFFLINE", font=self.font_status, text_color="#FF4557")
        status.pack(expand=True, fill='both')

    def set_status(self, status: Union[str, Tuple[int, int]]):

        # delete all widgets
        for widget in self.winfo_children():
            widget.destroy()

        if status == "off":
            self._offline_wiget()
        elif status == "on":
            self._online_wiget()
        elif status == "in":
            self._in_match_wiget()
        else:
            self._in_math_wiget(status)
