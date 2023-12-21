from customtkinter import *

from Helper.ImageHandel import open_gif_image
from Component.Structs import BaseMainFrame

PROGRESS = 1
ICON = 0


class Loading(BaseMainFrame):
    def __init__(self, master, text='', type_=PROGRESS, *arg, **kw):
        super().__init__(master, *arg, **kw)

        # init value
        self.index_img = 0
        self.type_ = type_

        # layout
        if type_ == ICON:
            self.login_icon = ImageAnimation(
                self, path=r"assets\img\Pulse-1s-200px.gif")
            self.login_icon.place(relx=0.5, rely=0.45, anchor=CENTER)
        elif type_ == PROGRESS:
            self.login_icon = CTkProgressBar(self, orientation="horizontal")
            self.login_icon.place(relx=0.5, rely=0.5,
                                  anchor=CENTER, relwidth=0.6)
            self.login_icon.set(0)

        self.content = CTkLabel(self, text=text, font=("Consolas", 15))
        self.content.place(relx=0.5, rely=0.6, anchor=CENTER, relwidth=0.6)

    def set_text(self, text):
        self.content.configure(text=text)

    def set_progress(self, value):
        # Set progress bar to specific value (range 0 to 1).
        if self.type_ == PROGRESS:
            self.login_icon.set(value)


class ImageAnimation(CTkLabel):
    def __init__(self, master, path, duration_s=1, width=40, height=40, *args, **kwargs):
        """_summary_

        Args:
            master (_type_): _description_
            path (str): path of file gif
            duration_s (float):
        """
        super().__init__(master, text='', *args, **kwargs)
        self.path = path
        images = open_gif_image(self.path)
        self.images = [CTkImage(img, size=(width, height)) for img in images]

        self.images_len = len(self.images)

        self.fps = (duration_s * 60) // self.images_len
        self.img_index = 0

        self.configure(image=self.images[self.img_index])
        self.after(self.fps, self.update_img)

    def update_img(self):
        self.img_index += 1
        if self.img_index >= self.images_len:
            self.img_index = 0

        self.configure(image=self.images[self.img_index])
        self.after(self.fps, self.update_img)

