import tkinter
import asyncio

from PIL import Image

from CTkToolTip import CTkToolTip
from CTkMessagebox import CTkMessagebox
from customtkinter import *

from Constant import Constant
from widgets.Structs import TabViewFrame
from widgets.ImageHandel import load_img


class Line(CTkEntry):
    def __init__(self, master, variable: tkinter.IntVar = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.variable = variable
        self.bind('<Key>', self.check_is_init)

    def check_is_init(self, *args):
        text: str = self.get()
        if text.isnumeric():
            self.variable.set(int(text))


class BaseSettingItem(CTkFrame):
    def __init__(self, master, title, des, height=50,fg_color="#333333" ,*args, **kwargs, ):
        super().__init__(master, fg_color=fg_color, height=height, *args, **kwargs)
        
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        self.setting = CTkLabel(self, text=title, font=CTkFont(
            size=17, weight="bold"), height=height)

        if des is not None:
            self.setting.configure(anchor=SW, height=height//2 + 3)
            self.setting.grid(row=0, column=0, sticky=SW, padx=10)

            self.des = CTkLabel(self, text=des, font=(
                None, 10), anchor=NW, height=height//2 - 3)
            self.des.grid(row=1, column=0, sticky=NW, padx=15)

        else:
            self.setting.grid(row=0, column=0, columnspan=2, padx=10, sticky=W)

class SettingItemSwitch(BaseSettingItem):
    def __init__(self, master, title, des , setting_value = None, height=50, *args, **kwargs):
        super().__init__(master, title , des, height)

        self.switch = CTkSwitch(
            self, width=36, onvalue=True, offvalue=False, variable=setting_value, text='')
        self.switch.grid(column=2, row=0, rowspan=2, sticky=E, padx=5)

class Dropdow(CTkFrame):
    def __init__(self, master, title, des , fg_color="#333333" ,*args, **kwargs, ):
        super().__init__(master, fg_color="transparent", height=50,*args, **kwargs)
        
        self.item = []
        self.height = 50
        self.current_height = 50
        self.show_ = False
        
        self.loop = asyncio.get_event_loop()
        
        self.summary = BaseSettingItem(self, title, des)
        self.summary.place(x = 0, y = 0, relwidth = 1)
        
        
        drop_dow = CTkImage(load_img(r'assets\img\arrow-down-d.png'), load_img(r'assets\img\arrow-down-l.png'))
        button = CTkButton(self.summary, text="", width=28, corner_radius=0, command=self.button_click, fg_color="transparent", hover=False, image=drop_dow)
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
        for i in range(self.current_height, target , abs(self.current_height - target)//5):
            self.configure(height=i)
            await asyncio.sleep(0.01)
        self.current_height = target
        self.configure(height=target)
        
        
    def show(self):
        self.loop.create_task(self._show())
    
    async def _hide(self):
        target = 50
        for i in range(self.current_height, target , -abs(self.current_height - target)//5):
            self.configure(height=i)
            await asyncio.sleep(0.01)

        self.current_height = target
        self.configure(height=target)
    
    def hide(self):
        self.loop.create_task(self._hide())
        
    def place_item(self):
        for i in self.item:
            pass
        
    def add_item(self, item: CTkBaseClass):
        self.item.append(item)
        self._render()
        
    def _render(self):
        for index, ele in enumerate(self.item):
            ele: CTkFrame
            y_pos = int((ele._current_height + 4) * (index + 1))
            ele.place(y = y_pos, relx = 0.05, relwidth = 0.95)

    def calculate_height(self):
        t = 50
        for i in self.item:
            # i: CTkFrame
            t += i._current_height
            t += 4
        return t


class Setting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # setup value
        self.setting = {}
        self.font = CTkFont('Consolas', 14, 'bold')
        self.height = 0
        self.width = 0

        # setup scrollable
        self.main_frame = CTkScrollableFrame(self, corner_radius=10)
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)
        self.main_frame.grid_columnconfigure((0, 2), weight=1, uniform='a')
        self.main_frame.grid_columnconfigure(1, weight=2, uniform='a')

        save_img = CTkImage(load_img('./assets/img/save-d.png'),
                            load_img('./assets/img/save-l.png'))

        self.save_button = CTkButton(self, text='', height=40, width=40, image=save_img, fg_color="#2B2B2B",
                                     bg_color="#333333", command=self.save_button_click_handel)

        self.render_setting()
        Constant.App_Setting.add_callback(self.setting_update)
        self.bind('<Configure>', self.update_pos)

    def setting_update(self, **args):
        for key, value in Constant.App_Setting.get().items():
            # self.setting[key].set(value["value_"])
            pass

    def save_button_click_handel(self):
        CTkMessagebox(title="Success", message="Save Complicit")
        Constant.App_Setting.get()

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.save_button.place(x=configure.width - 35, y=30, anchor=CENTER)

    def render_setting(self):
        run_with_window = SettingItemSwitch(self.main_frame, "startup with window", None, Constant.App_Setting['startup'])
        run_with_window.grid(row=0, column=1, sticky=NSEW, pady=2)

        #  
        run_on_background = SettingItemSwitch(self.main_frame, "run on background", "Keep launcher run when your in game", Constant.App_Setting['run-on-background'])
        run_on_background.grid(row=1, column=1, sticky=NSEW, pady=2)
 
 
        # 
        quick_access = Dropdow(self.main_frame, "Quick access", None)
        quick_access.grid(row=2, column=1, sticky=NSEW, pady=2)
        
        quick_access.add_item(SettingItemSwitch(quick_access, "Quick access", "Create shortcut of each account", Constant.App_Setting['craft-shortcut']))
        quick_access.add_item(SettingItemSwitch(quick_access, "Allows start menu", "Allows create shortcut to start menu", Constant.App_Setting['allows-start-menu']))
        quick_access.add_item(SettingItemSwitch(quick_access, "Allows desktop", "Allows create shortcut to desktop", Constant.App_Setting['allows-desktop']))
        
        
        #    
        overwrite_setting = Dropdow(self.main_frame, "Game Setting", None)
        overwrite_setting.grid(row=3, column=1, sticky=NSEW, pady=2)
        
        overwrite_setting.add_item(SettingItemSwitch(overwrite_setting, "overwrite setting", "overwrite your setting in game", Constant.App_Setting['overwrite-setting']))
        overwrite_setting.add_item(SettingItemSwitch(overwrite_setting, "backup setting", "set back setting, requires run on background", Constant.App_Setting['backup-setting']))

    def show(self):
        super().show()
