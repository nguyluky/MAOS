import tkinter as tk
import urllib.request

from customtkinter import *
from ctypes import windll, c_int, sizeof, byref


class Update(CTkToplevel):
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("500x100")
        self.resizable(0, 0)
        self.title('Download update')
        self.url = url
        HWND = windll.user32.GetParent(self.winfo_id())
        color = 0x20202000
        windll.dwmapi.DwmSetWindowAttribute(
            HWND,
            35,
            byref(c_int(color)),
            sizeof(c_int)
        )

        self.progressbar_var = tk.DoubleVar(self, 0.0)

        self.progressbar = CTkProgressBar(self, variable=self.progressbar_var)
        self.progressbar.place(relx=.5, rely=.5, relwidth=.9, anchor=CENTER)

        self.protocol("WM_DELETE_WINDOW", self.quit_handel)

    def quit_handel(self):
        pass

    def download_file_from_url(self, url, file_path="install"):
        resp = urllib.request.urlopen(url)
        length = resp.getheader('content-length')
        if length:
            length = int(length)
            block_size = max(4096, length // 100)
        else:
            block_size = 1000000  # just made something up

        print(length, block_size)

        buf = io.BytesIO()
        size = 0
        while True:
            buf1 = resp.read(block_size)
            if not buf1:
                break
            buf.write(buf1)
            size += len(buf1)
            if length:
                self.progressbar_var.set(size / length)

        with open(file_path, "wb+") as file:
            file.write(buf.getbuffer())
