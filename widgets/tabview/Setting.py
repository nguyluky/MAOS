import tkinter

from PIL import Image

from CTkToolTip import CTkToolTip
from CTkMessagebox import CTkMessagebox
from customtkinter import *

from Constant import Constant
from widgets.Structs import TabViewFrame
from widgets.ImageHandel import load_img

# TODO format setting file


class Setting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # setup value
        self.setting = {}
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
        Constant.App_Setting.add_callback(self.setting_update)
        self.bind('<Configure>', self.update_pos)

    def setting_update(self, **args):
        for key, value in Constant.App_Setting.get().items():
            self.setting[key].set(value["value_"])

    def save_button_click_handel(self):
        CTkMessagebox(title="Success", message="Save Complicit")
        for key, value in self.get_setting().items():
            Constant.App_Setting.set(key, value)

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.save_button.place(x=configure.width - 35, y=30, anchor=CENTER)

    def render_setting(self):
        index = 0
        for key, value in Constant.App_Setting.get().items():
            displayName = value["displayName"]
            type_ = value["type"]
            value_ = value["value_"]
            description = value["description"]

            text = CTkLabel(self.main_frame, text=displayName, font=self.font)
            text.grid(row=index, column=1, sticky="w", ipady=5)

            if type_ == 0:
                ctkValue = tkinter.BooleanVar(self, 1 if value_ else 0)
                frame = CTkSwitch(self.main_frame, text='', onvalue=1,
                                  offvalue=0, variable=ctkValue, width=50)

            elif type_ == 1:
                # TODO make a new class to handel entry int
                ctkValue = tkinter.IntVar(self, value_)
                frame = CTkEntry(
                    self.main_frame, textvariable=ctkValue, width=50)

            if description:
                CTkToolTip(text, message=description)

            frame.grid(row=index, column=3)
            self.setting[key] = ctkValue
            index += 1

    def get_setting(self):
        setting = {}
        de = Constant.App_Setting.get()
        for key, value in self.setting.items():
            if isinstance(de[key], bool):
                setting[key] = value.get()
            else:
                setting[key] = value.get()
        return setting

    def show(self):
        super().show()
