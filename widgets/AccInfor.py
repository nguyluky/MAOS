import inspect
import asyncio
import tkinter as tk
import logging

from asyncio.events import AbstractEventLoop

from widgets.AccStatus import *
from widgets.ImageHandel import *
from ValLib import ExtraAuth, EndPoints
from Constant import Constant
from helper import get_acc_infor, check_account_status


URL_PLYER_CARD_DEF = "https://media.valorant-api.com/playercards/c89194bd-4710-b54e-8d6c-60be6274fbb2/displayicon.png"

logger = logging.getLogger("main_app")


class AccInfor(CTkFrame):
    def __init__(self, master, corner_radius,change_account_click=None,*arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)

        # init frame
        self.height = self.master["height"]
        self.corner_radius = corner_radius
        self.configure(height=self.height)
        
        # setup value
        self.values = []
        self.loop = asyncio.get_event_loop()

        # init image
    
        # setup value
        self.name = tk.StringVar(self, '')
        self.title = tk.StringVar(self, '')

        # avt img
        self.avt_img: CTkImage = None
        self.label_avt: CTkLabel = CTkLabel(self, text="", width=int(self.height * 0.7), height=int(self.height * 0.7))
        self.label_avt.pack(side=LEFT, padx=int(self['height'] * 0.3 / 2), pady=int(self['height'] * 0.3 / 2))

        # player name and title widget
        frame_name = CTkFrame(self, fg_color="transparent")
        frame_name.pack(side=LEFT)

        font_name = CTkFont('Consolas', 20, "bold")
        font_title = CTkFont('Consolas', 14, "normal")

        name_text = CTkLabel(frame_name, textvariable=self.name, anchor="sw", font=font_name)
        name_text.pack(expand=True, fill='both')

        title_text = CTkLabel(frame_name, textvariable=self.title, anchor="nw", font=font_title)
        title_text.pack(fill='both', expand=True)

        # acc status widget
        self.acc_status = AccStatus(self, OFFLINE)
        self.acc_status.place(relx=.7, rely=0.5, anchor=CENTER)
        self.acc_status.set_status('off')

        img = CTkImage(load_img(r'assets\img\menu-d.png'), load_img(r'assets\img\menu-l.png'))
        self.change_account = CTkButton(self, height=40 , width=40, text='' , image=img, command=change_account_click, hover=False, fg_color="transparent")
        
        self.bind('<Configure>', self.update_pos)
        self.after(Constant.App_Setting['refresh-time'], lambda *args: self.loop.create_task(self.update_status()))
        
    async def update_status(self):
        acc: EndPoints = Constant.Current_Acc.get()
        if acc:
            status = await check_account_status(acc)
            self.acc_status.set_status(status)
        self.after(Constant.App_Setting['refresh-time'] * 1000 , lambda *args: self.loop.create_task(self.update_status()))
        
    def update_pos(self, configure):
        width = configure.width
        height = configure.height
        
        self.change_account.place(x=width - 10, y=(height - 40) // 2, anchor=NE)
    
    def update_account(self):
        self.loop.create_task(self.update_status())
        self.loop.create_task(self.render_acc_infor(Constant.Current_Acc.get()))
    
    async def render_acc_infor(self, pvp: EndPoints):
        name, avt, title = await get_acc_infor(pvp)
        self._set_avt(avt)
        self._set_title(title)
        self._set_name(name)

    def _set_name(self, name):
        self.name.set(name)
        
    def _set_title(self, title):
        self.title.set(title)
        
    def _set_avt(self, avt_url):
        self.loop.create_task(self.get_avt_img_and_set(avt_url))
    
    async def get_avt_img_and_set(self, avt_url):
        img_pil = await async_load_img_from_url(avt_url)
        self.avt_img = CTkImage(cropping_image_in_a_circular(img_pil), size=(int(self.height * 0.7), int(self.height * 0.7)))
        self.label_avt.configure(image = self.avt_img)

    