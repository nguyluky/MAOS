import tkinter

from PIL import Image
from Constant import Constant
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from widgets.Structs import TabViewFrame
from widgets.ImageHandel import load_img


class Setting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # setup value
        self.setting = []
        self.font = CTkFont('Consolas', 14, 'bold')
        self.height = 0
        self.width = 0

        # setup scrollable
        self.main_frame = CTkScrollableFrame(self, corner_radius=10)
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)
        self.main_frame.grid_columnconfigure((0, 4), weight=3)
        self.main_frame.grid_columnconfigure((1, 2, 3), weight=1)

        save_img = CTkImage(load_img('./assets/img/save-d.png'),
                            load_img('./assets/img/save-l.png'))

        self.save_button = CTkButton(self, text='', height=40, width=40, image=save_img, fg_color="#2B2B2B",
                                     bg_color="#333333", command=self.save_button_click_handel)

        self.render_setting()
        self.bind('<Configure>', self.update_pos)

    def save_button_click_handel(self):
        CTkMessagebox(title="Success", message="Save Complicit")
        Constant.App_Setting.set(self.get_setting())

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.save_button.place(x=configure.width - 35, y=30, anchor=CENTER)

    def render_setting(self):
        index = 0
        for key, value in Constant.App_Setting.get().items():

            text = CTkLabel(self.main_frame, text=key, font=self.font)
            text.grid(row=index, column=1, sticky="w", ipady=5)

            if isinstance(value, bool):
                tk_value = tkinter.IntVar(self, 1 if value else 0)
                widget = CTkSwitch(self.main_frame, onvalue=1,
                                   offvalue=0, text='', variable=tk_value)

            elif isinstance(value, int):
                tk_value = IntVar(self, value)
                widget = CTkEntry(self.main_frame, width=50,
                                  textvariable=tk_value)

            self.setting.append((key, tk_value))
            widget.grid(row=index, column=3, sticky="w")

            index += 1

    def get_setting(self):
        setting = {}
        de = Constant.App_Setting.get()
        for key, value in self.setting:
            if isinstance(de[key], bool):
                setting[key] = value.get() == 1
            else:
                setting[key] = value.get()
        return setting

    def show(self):
        super().show()
