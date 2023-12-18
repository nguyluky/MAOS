import asyncio
import json
import logging

from asyncio.events import AbstractEventLoop
from CTkToolTip import CTkToolTip
from customtkinter import *
from CTkMessagebox import CTkMessagebox

from Helper.Constant import Constant
from ValLib import EndPoints, ExtraAuth
from Widgets.Structs import TabViewFrame
from Widgets.ImageHandel import load_img


logger = logging.getLogger("main_app")


class ValorantSetting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # init value
        self.loop: AbstractEventLoop = asyncio.get_event_loop()
        self.setting_valorant: dict = {}
        self.popup_is_show = False
        self.height = 0
        self.width = 0
        self.buttons = {}

        # init layout
        self.setting_view = CTkTextbox(self, corner_radius=15)
        self.setting_view.place(x=0, y=0, relwidth=1, relheight=1)

        load_img_ = CTkImage(load_img('./assets/img/downloading-updates-d.png'),
                             load_img('./assets/img/downloading-updates-l.png'))
        save_img = CTkImage(load_img('./assets/img/save-d.png'),
                            load_img('./assets/img/save-l.png'))

        self.load_button = CTkButton(self, text='', height=40, width=40, image=load_img_, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.load_button_click_handel)
        CTkToolTip(self.load_button, "load setting from account")

        self.save_button = CTkButton(self, text='', height=40, width=40, image=save_img, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.save_button_click_handel)
        CTkToolTip(self.save_button, "save setting to default")
        self.frame_acc = CTkFrame(self, bg_color="#1D1E1E")

        # init event
        self.bind('<Configure>', self.update_pos)

    def load_button_click_handel(self):
        if self.popup_is_show:
            self.hidden_popup()
            return

        self.popup_acc_render()
        self.show_popup()

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.load_button.place(x=configure.width - 35, y=30, anchor=CENTER)
        self.save_button.place(x=configure.width - 35, y=80, anchor=CENTER)

    def show_popup(self):
        self.frame_acc.place(x=self.width - 55, y=10, anchor=NE)
        self.popup_is_show = True

    def hidden_popup(self):
        self.frame_acc.place_forget()
        self.popup_is_show = False

    async def click_handle(self, user_name):
        for endpoint in Constant.EndPoints:
            endpoint: EndPoints
            if user_name == endpoint.auth.username:
                logger.debug(f'get setting {endpoint.auth.username}')
                self.setting_view.delete('0.0', 'end')
                setting = await endpoint.Setting.async_Fetch_Preference()
                self.setting_view.insert('0.0', json.dumps(setting, indent=4))

        self.hidden_popup()

    def add_account(self, acc: ExtraAuth):
        text = CTkButton(self.frame_acc, text=acc.username, fg_color="transparent",
                         command=lambda: self.handle_click_change_account(acc))
        self.buttons[acc.user_id] = text

    def handle_click_change_account(self, acc):
        self.loop.create_task(self.click_handle(acc.username))

    def popup_acc_render(self):
        for i in Constant.Accounts:
            if self.buttons.get(i.user_id, None) is None:
                self.add_account(i)

        for i in self.buttons.values():
            i.pack(fill=X, padx=10, pady=5)

    def save_button_click_handel(self):
        logger.debug("game setting save")
        setting = self.setting_view.get('0.0', END)
        # print(setting)
        Constant.Setting_Valorant = json.loads(setting)
        CTkMessagebox(title="Success", message="Save Complicit")

    def show(self):
        super().show()
        self.setting_view.insert('0.0', json.dumps(
            Constant.Setting_Valorant, indent=4))
