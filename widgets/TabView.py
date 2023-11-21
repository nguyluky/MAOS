from typing import Union, Tuple

from CTkToolTip import CTkToolTip
from customtkinter import *

from widgets.ImageHandel import *
from widgets.Structs import TabViewFrame

from widgets.tabview.MatchHistory import MatchHistory
from widgets.tabview.Shop import Shop
from widgets.tabview.ValorantSetting import ValorantSetting
from widgets.tabview.Setting import Setting


class TabView(CTkFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.button_icon = {
            "shop": CTkImage(load_img("./img/shop-d.png"), load_img("./img/shop-l.png")),
            "Valorant Setting": CTkImage(load_img("./img/curly-brackets-d.png"),
                                         load_img("./img/curly-brackets-l.png")),
            "match": CTkImage(load_img("./img/feed-d.png"), load_img("./img/feed-l.png")),
            "setting": CTkImage(load_img("./img/support-d.png"), load_img("./img/support-l.png"))
        }
        # tab_title_view
        self.tab_title = TabMaster(self, fg_color="transparent", orientation=HORIZONTAL,
                                   values=self.button_icon,
                                   command=self.tab_handel, corner_radius=self._corner_radius)
        self.tab_title.pack(side=LEFT, fill=BOTH, pady=7, padx=7)

        # window view
        self.main_view = CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side=LEFT, fill=BOTH, expand=True, pady=7, padx=7)

        self.frame_ = {
            "shop": Shop(self.main_view),
            "Valorant Setting": ValorantSetting(self.main_view),
            "match": MatchHistory(self.main_view),
            "setting": Setting(self.main_view)
        }

        self.hidden_all_frame_()
        var = self.frame_["shop"]
        var.show()

    def tab_handel(self, tab):
        for key in self.button_icon.keys():
            if self.button_icon[key] is tab:
                self.hidden_all_frame_()
                frame = self.frame_.get(key, None)
                frame.show()

    def hidden_all_frame_(self):
        for i in self.frame_.values():
            i.hidden()


class TabMaster(CTkFrame):
    def __init__(self, master, orientation, values: Union[Tuple[str], tuple[CTkImage], dict[str, CTkImage]],
                 corner_radius=10,
                 hover_color=None, command=None,
                 height=50, width=50, *args, **kw):
        super().__init__(master, *args, **kw)
        self.hover_color = hover_color if hover_color is not None else ThemeManager.theme["CTkButton"]["hover_color"]
        self.width = width
        self.height = height
        self.orientation = orientation
        self.bg_color = self._detect_color_of_master()
        if isinstance(values, dict):
            self.value_selenium = list(values.keys())[0]
        else:
            self.value_selenium = values[0]
        self.values = values
        self.command = command
        self.corner_radius = corner_radius

        self.list_button = [self.craft_button(e) for e in values]

        for e in self.list_button:
            if self.orientation == HORIZONTAL:
                e.pack(side=TOP, pady=2)
            else:
                e.pack(side=LEFT, padx=2)

    def _click_handel(self, ele):
        # xóa toàn bộ bg
        for e in self.list_button:
            e.configure(fg_color=self.bg_color)

        # lấy nút bấm và thay đổi bg
        if isinstance(self.values, dict):
            list_ = list(self.values.keys())
            index = list_.index(ele)
        else:
            index = self.values.index(ele)
        self.list_button[index].configure(fg_color=self.hover_color)
        if self.command is not None:
            if isinstance(self.values, dict):
                self.command(self.values[ele])
            else:
                self.command(ele)

    def craft_button(self, e):
        if isinstance(self.values, dict):
            button = CTkButton(self, image=self.values[e], text='', fg_color=self.bg_color,
                               corner_radius=self.corner_radius)
            CTkToolTip(button, e)
        elif isinstance(e, str):
            button = CTkButton(self, text=e, fg_color=self.bg_color, corner_radius=self.corner_radius)
        elif isinstance(e, CTkImage):
            button = CTkButton(self, image=e, text='', fg_color=self.bg_color, corner_radius=self.corner_radius)

        button.configure(command=lambda: self._click_handel(e))

        if e == self.value_selenium:
            button.configure(fg_color=self.hover_color)

        if self.orientation == HORIZONTAL:
            unit = self.width
            button.configure(height=unit, width=unit)
        elif self.orientation == VERTICAL:
            unit = self.height
            button.configure(height=unit, width=unit)

        return button
