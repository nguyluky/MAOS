from customtkinter import *

from asyncio.events import AbstractEventLoop
from widgets.ImageHandel import open_gif_image

PROGRESS = 1
ICON = 0


class Loaing(CTkFrame):
    def __init__(self, master, text='', type_=PROGRESS, height=30, width=30, *arg, **kw):
        super().__init__(master, *arg, **kw)
        self.index_img = 0

        self.type_ = type_

        if type_ == ICON:
            images = open_gif_image("img/Pulse-1s-200px.gif")
            self.img_count = len(images)
            self.ms = (60 * 2) // self.img_count
            self.CTkImages = [CTkImage(img, size=(width, height)) for img in images]
            self.login_icon = CTkLabel(self, text='', image=self.CTkImages[self.index_img])
            self.login_icon.place(relx=0.5, rely=0.45, anchor=CENTER)
        elif type_ == PROGRESS:
            self.login_icon = CTkProgressBar(self, orientation="horizontal")
            self.login_icon.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.6)
            self.login_icon.set(0)

        self.content = CTkLabel(self, text=text)
        self.content.place(relx=0.5, rely=0.6, anchor=CENTER, relwidth=0.6)

        if type_ == ICON:
            self.after(self.ms, self.animation)

    def animation(self):
        self.index_img += 1
        if self.index_img >= self.img_count:
            self.index_img = 0
        self.login_icon.configure(image=self.CTkImages[self.index_img])
        self.after(self.ms, self.animation)

    def set_text(self, text):
        self.content.configure(text=text)

    def setprogress(self, value):
        # Set progress bar to specific value (range 0 to 1).
        if self.type_ == PROGRESS:
            self.login_icon.set(value)
