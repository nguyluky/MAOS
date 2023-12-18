import tkinter as tk
import asyncio
import logging

from CTkMessagebox import CTkMessagebox

from ValLib import EndPoints, ExtraAuth
from Helper.Constant import Constant
from Widgets.Structs import BaseMainFrame
from Widgets.ImageHandel import load_img, async_load_img_from_url, cropping_image_in_a_circular
from Widgets.AccStatus import *
from Helper.helper import get_acc_info

AVT_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS\\Avt')
URL_PLAYER_CARD_DEF = "https://media.valorant-api.com/playercards/c89194bd-4710-b54e-8d6c-60be6274fbb2/displayicon.png"

logger = logging.getLogger('main_app')


class AccountSwitch(BaseMainFrame):
    def __init__(self, master, corner_radius, close_click=None, add_click=None, *arg, **kw):
        super().__init__(master, *arg, **kw)

        # init value
        self.loop = asyncio.get_event_loop()
        self.frame_acc = {}
        self.close_click = close_click
        self.add_click = add_click

        self.frame_center = CTkScrollableFrame(
            self, corner_radius=corner_radius)
        self.frame_center.place(anchor="c", relx=.5,
                                rely=.5, relwidth=0.6, relheight=0.7)
        self.frame_center.columnconfigure(0, weight=1)

        close_img = CTkImage(load_img(r'assets\img\close-d.png'),
                             load_img(r'assets\img\close-l.png'))
        self.close_button = CTkButton(
            self, image=close_img, command=close_click, text='', fg_color="transparent", height=40, width=40)

        add_img = CTkImage(load_img(r'assets\img\add-d.png'),
                           load_img(r'assets\img\add-l.png'), size=(40, 40))
        self.add_button = CTkButton(self.frame_center, height=50, width=50,
                                    image=add_img, command=self.add_click, text='', fg_color="transparent")

        Constant.EndPoints.add_callback(self.endpoint_event)

    async def endpoint_event(self, mod, value):
        await self._add(value)

    def _clear(self):
        for i in self.frame_acc.values():
            i.destroy()

    def render_(self):
        for index, i in enumerate(self.frame_acc.values()):
            i.grid(row=index, column=0)

        self.add_button.grid(row=len(self.frame_acc.values()), column=0)

    def login_handel(self, endpoint: EndPoints):
        logger.debug(f'login at {endpoint.auth.username}')
        if Constant.Current_Acc.get() != endpoint:
            Constant.Current_Acc.set(endpoint)
        self.close_click()

    def remove_handel(self, endpoint: EndPoints):

        msg = CTkMessagebox(title="Remove?", message=f"Do you want to remove {endpoint.auth.username}?",
                            icon="question", option_1="Cancel", option_2="No", option_3="Yes")

        response = msg.get()

        if response == "Yes":
            logger.debug(f"remove account {endpoint.auth.username}")
            for i in self.frame_acc.values():
                i.grid_forget()

            self.frame_acc.pop(endpoint.auth.user_id)
            self.render_()

            for i in Constant.Accounts:
                if i.user_id == endpoint.auth.user_id:
                    Constant.Accounts.remove(i)
                    break

    async def _add(self, i: EndPoints):
        if self.frame_acc.get(i.auth.user_id, None) is None:
            name, avt, title = await get_acc_info(i)
            frame = AccView(self.frame_center, 20, name, avt, title, command_login=lambda: self.login_handel(
                i), command_remove=lambda: self.remove_handel(i))
            self.frame_acc[i.auth.user_id] = frame

    def show(self):
        super().show()
        self.close_button.place(relx=1, y=0, anchor=NE)
        self.render_()


class AccView(CTkFrame):
    def __init__(self, master, corner_radius, name='', avt=URL_PLAYER_CARD_DEF, title='', command_login=None,
                 command_remove=None, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, height=50, *arg, **kw)

        # setup value
        self.name = tk.StringVar(self, name)
        self.title = tk.StringVar(self, title)
        self.loop = asyncio.get_event_loop()

        # font
        font_name = CTkFont('Consolas', 20, "bold")
        font_title = CTkFont('Consolas', 14, "normal")

        # avt img
        self.avt_img: CTkImage = None
        self.label_avt: CTkLabel = CTkLabel(self, text="")
        self.set_avt(url=avt)
        self.label_avt.pack(side=LEFT, padx=int(
            self['height'] * 0.3 / 2), pady=int(self['height'] * 0.3 / 2))

        # player name and title widget
        frame_name = CTkFrame(self, fg_color="transparent")
        frame_name.pack(side=LEFT)

        name_text = CTkLabel(frame_name, textvariable=self.name,
                             anchor="sw", font=font_name, width=250)
        name_text.pack(expand=True, fill='both')

        title_text = CTkLabel(
            frame_name, textvariable=self.title, anchor="nw", font=font_title)
        title_text.pack(fill='both', expand=True)

        # acc status widget

        # buton login
        img = CTkImage(load_img(r'assets\img\login-d.png'),
                       load_img(r'assets\img\login-l.png'))
        button_login = CTkButton(self, text='', image=img, hover=True,
                                 height=40, width=40, fg_color="transparent", command=command_login)
        button_login.pack(side=LEFT, padx=(30, 0))

        # remove account
        img_remove = CTkImage(
            load_img(r'assets\img\close-d.png'), load_img(r'assets\img\close-l.png'))
        button_remove = CTkButton(self, text='', image=img_remove, hover=True,
                                  height=40, width=40, fg_color="transparent", command=command_remove)
        button_remove.pack(side=LEFT)

    def _size_update(self, height):
        if self.avt_img is not None:
            self.avt_img.configure(size=(int(height * 0.7), int(height * 0.7)))

    async def _set_avt(self, url=None, path=None):
        if url is not None:
            img = await async_load_img_from_url(url)
            img_pil = cropping_image_in_a_circular(img)
        elif path is not None:
            img_pil = load_img(path)
        else:
            return

        for i in Constant.Accounts:
            i: ExtraAuth
            if i.username == self.name.get():
                img_pil.save(os.path.join(
                    AVT_PATH, f"{i.user_id}.ico"), format='ICO')
        size = (30, 30)
        self.avt_img = CTkImage(img_pil, size=size if (
                size[0] != 0 or size[1] != 0) else img_pil.size)
        self._size_update(self['height'])
        self.label_avt.configure(image=self.avt_img)

    def set_avt(self, url=None, path=None):
        self.loop.create_task(self._set_avt(url, path))

    def set_name(self, name: str):
        self.name.set(name)

    def set_title(self, text: str):
        self.title.set(text)
