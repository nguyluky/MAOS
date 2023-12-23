import asyncio
import io
import tkinter as tk
import threading
import urllib.request
import subprocess

from Helper.helper import TEMP_PATH
from customtkinter import *
from ctypes import windll, c_int, sizeof, byref

loop = asyncio.get_event_loop()

path_install = TEMP_PATH + "\\install.exe"


class Update(CTk):
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("500x100")
        self.resizable(0, 0)
        self.title('Download update')
        self.url = url
        self.run = True
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

        # threading.Thread(target=download_file_from_url, args=(self.url, "install.exe",self.progressbar_var,)).start()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.download_file_from_url(self.url))

    async def download_file_from_url(self, url):
        print("start down")
        await self.loop.run_in_executor(None, self._download_file_url, url)
        self.event_generate("<<Downloaded_successfully>>")
        await self.complete()

    def quit_handel(self):
        pass

    async def show(self):
        while self.run:
            self.update()
            await asyncio.sleep(0.1)

        subprocess.Popen(path_install)

    def _download_file_url(self, url):
        resp = urllib.request.urlopen(url)
        length = resp.getheader('content-length')
        if length:
            length = int(length)
            block_size = max(4096, length // 100)
        else:
            block_size = 1000000  # just made something up

        # print(length, block_size)

        buf = io.BytesIO()
        size = 0
        while True:
            buf1 = resp.read(block_size)
            if not buf1:
                break
            buf.write(buf1)
            size += len(buf1)
            if length:
                # pr_var.set(size / length)
                loop.create_task(self.update_value(size / length))
                print(size / length)

        with open(path_install, "wb+") as file:
            file.write(buf.getbuffer())

    async def update_value(self, value):
        self.progressbar_var.set(value)

    async def complete(self):
        self.run = False

if __name__ == "__main__":
    app = Update("https://github.com/nguyluky/MAOS/releases/download/1.0.4/mysetup.exe")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.show())
