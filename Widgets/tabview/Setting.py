import logging
import tkinter
import asyncio

from CTkMessagebox import CTkMessagebox
from customtkinter import *

from ValLib import ExtraAuth

from Helper.Constant import Constant
from Widgets.Structs import TabViewFrame
from Widgets.ImageHandel import load_img

logger = logging.getLogger("main_app")


class Line(CTkEntry):
    def __init__(self, master, variable: tkinter.IntVar = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.variable = variable
        self.bind('<Key>', self.check_is_init)

    def check_is_init(self, *_):
        text: str = self.get()
        if text.isnumeric():
            self.variable.set(int(text))


class BaseSettingItem(CTkFrame):
    def __init__(self, master, title, des, height=50, fg_color="#333333", *args, **kwargs):
        super().__init__(master, fg_color=fg_color, height=height, *args, **kwargs)

        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        self.setting = CTkLabel(self, text=title, font=CTkFont(
            size=17, weight="bold"), height=height)

        if des is not None:
            self.setting.configure(anchor=SW, height=height // 2 + 3)
            self.setting.grid(row=0, column=0, sticky=SW, padx=10)

            self.des = CTkLabel(self, text=des, font=(
                None, 10), anchor=NW, height=height // 2 - 3)
            self.des.grid(row=1, column=0, sticky=NW, padx=15)

        else:
            self.setting.grid(row=0, column=0, columnspan=2, padx=10, sticky=W)

    def add_addon(self, widget: CTkBaseClass):
        widget.grid(column=2, row=0, rowspan=2, sticky=E, padx=5)


class SettingItemSwitch(BaseSettingItem):
    def __init__(self, master, title, des, setting_value=None, height=50, *args, **kwargs):
        super().__init__(master, title, des, height, *args, **kwargs)

        self.switch = CTkSwitch(
            self, width=36, onvalue=True, offvalue=False, variable=setting_value, text='')

        self.add_addon(self.switch)


class DropDow(CTkFrame):
    def __init__(self, master, title, des, *args, **kwargs, ):
        super().__init__(master, fg_color="transparent", height=50, *args, **kwargs)

        self.items = []
        self.height = 50
        self.current_height = 50
        self.show_ = False

        self.loop = asyncio.get_event_loop()

        self.summary = BaseSettingItem(self, title, des)
        self.summary.place(x=0, y=0, relwidth=1)

        drop_dow = CTkImage(load_img(r'assets\img\arrow-down-d.png'), load_img(r'assets\img\arrow-down-l.png'))
        button = CTkButton(self.summary, text="", width=28, corner_radius=0, command=self.button_click,
                           fg_color="transparent", hover=False, image=drop_dow)
        button.grid(column=2, row=0, rowspan=2, sticky=E, padx=15)

    def button_click(self):
        if self.show_:
            self.hide()
            self.show_ = not self.show_
            return
        self.show_ = not self.show_
        self.show()

    async def _show(self):
        target = int(self.calculate_height())
        for i in range(self.current_height, target, abs(self.current_height - target) // 5):
            self.configure(height=i)
            await asyncio.sleep(0.01)
        self.current_height = target
        self.configure(height=target)

    def show(self):
        self.loop.create_task(self._show())

    async def _hide(self):
        target = 50
        for i in range(self.current_height, target, -abs(self.current_height - target) // 5):
            self.configure(height=i)
            await asyncio.sleep(0.01)

        self.current_height = target
        self.configure(height=target)

    def hide(self):
        self.loop.create_task(self._hide())

    def add_item(self, item: CTkBaseClass):
        self.items.append(item)
        self._render()

    def _render(self):
        for index, ele in enumerate(self.items):
            ele: CTkFrame
            y_pos = int((ele._current_height + 4) * (index + 1))
            ele.place(y=y_pos, relx=0.05, relwidth=0.95)

    def calculate_height(self):
        t = 50
        for i in self.items:
            i: CTkFrame
            t += i._current_height
            t += 4
        return t


class SettingItemDropDownMenu(BaseSettingItem):
    def __init__(self, master, title, des, values=None, setting_value=None, height=50, *args, **kwargs):
        super().__init__(master, title, des, height, *args, **kwargs)

        if values is None:
            values = []
        self.DropDown = CTkComboBox(self,
                                    values=values,
                                    variable=setting_value)
        self.add_addon(self.DropDown)

    def configure(self, require_redraw=False, **kwargs):
        if "values" in kwargs:
            self.DropDown.configure(values=kwargs['values'])
        else:
            super().configure(require_redraw, **kwargs)


class Setting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # setup value
        self.default_accout: SettingItemDropDownMenu = None
        self.setting = {}
        self.font = CTkFont('Consolas', 14, 'bold')
        self.height = 0
        self.width = 0

        self.list_account = []
        for i in Constant.Accounts:
            i: ExtraAuth
            self.list_account.append(i.username)

        # setup scrollable
        self.main_frame = CTkScrollableFrame(self, corner_radius=10)
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)
        self.main_frame.grid_columnconfigure((0, 2), weight=1, uniform='a')
        self.main_frame.grid_columnconfigure(1, weight=3, uniform='a')

        self.render_setting()
        Constant.Accounts.add_callback(self.accout_change)

    def accout_change(self, *args):
        self.list_account.clear()
        for i in Constant.Accounts:
            self.list_account.append(i.username)

        self.default_accout.configure(values=self.list_account)

    def render_setting(self):
        self.default_accout = SettingItemDropDownMenu(self.main_frame, "Default account", None, self.list_account,
                                                      Constant.App_Setting.default_account)

        self.default_accout.grid(row=0, column=1, sticky=NSEW, pady=2)

        run_with_window = SettingItemSwitch(self.main_frame, "Startup with window", None,
                                            Constant.App_Setting.startup)
        run_with_window.grid(row=1, column=1, sticky=NSEW, pady=2)

        #  
        run_on_background = SettingItemSwitch(self.main_frame, "Run on background",
                                              "Keep launcher run when your in game",
                                              Constant.App_Setting.run_on_background)
        run_on_background.grid(row=2, column=1, sticky=NSEW, pady=2)

        # 
        quick_access = DropDow(self.main_frame, "Quick access", None)
        quick_access.grid(row=3, column=1, sticky=NSEW, pady=2)

        quick_access.add_item(SettingItemSwitch(quick_access, "Quick access", "Create shortcut of each account",
                                                Constant.App_Setting.craft_shortcut))
        quick_access.add_item(
            SettingItemSwitch(quick_access, "Allows start menu", "Allows create shortcut to start menu",
                              Constant.App_Setting.allows_start_menu))
        quick_access.add_item(SettingItemSwitch(quick_access, "Allows desktop", "Allows create shortcut to desktop",
                                                Constant.App_Setting.allows_desktop))

        #    
        overwrite_setting = DropDow(self.main_frame, "Game Setting", None)
        overwrite_setting.grid(row=4, column=1, sticky=NSEW, pady=2)

        overwrite_setting.add_item(
            SettingItemSwitch(overwrite_setting, "overwrite setting", "overwrite your setting in game",
                              Constant.App_Setting.overwrite_setting))
        overwrite_setting.add_item(SettingItemSwitch(overwrite_setting, "backup setting", "set back setting",
                                                     Constant.App_Setting.backup_setting))

    def show(self):
        super().show()
