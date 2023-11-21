import inspect
import asyncio
import tkinter as tk
import logging

from asyncio.events import AbstractEventLoop

from widgets.AccStatus import *
from widgets.ImageHandel import *
from ValLib import ExtraAuth, EndPoints
from Constant import Constant

URL_PLYER_CARD_DEF = "https://media.valorant-api.com/playercards/c89194bd-4710-b54e-8d6c-60be6274fbb2/displayicon.png"

logger = logging.getLogger("main_app")

save_path = os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS\\Avt')

class Acc(CTkFrame):
    def __init__(self, master, corner_radius, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)

        # init frame
        self.configure(fg_color=self._detect_color_of_master())
        self.configure(bg_color=self.winfo_toplevel()["background"])

        # setup value
        self.name = tk.StringVar(self, '')
        self.title = tk.StringVar(self, '')

        # avt img
        self.avt_img: CTkImage = None
        self.label_avt: CTkLabel = CTkLabel(self, text="")
        self.label_avt.pack(side=LEFT, padx=int(self['height'] * 0.3 / 2), pady=int(self['height'] * 0.3 / 2))
        self.set_avt()

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

    def _size_update(self, height):
        if self.avt_img is not None:
            self.avt_img.configure(size=(int(height * 0.7), int(height * 0.7)))

    async def _set_avt(self, url=URL_PLYER_CARD_DEF, path=None):
        if url is not None:
            img = await async_load_img_from_url(url)
            img_pil = cropping_image_in_a_circular(img)
        elif path is not None:
            img_pil = load_img(path)
        else:
            raise KeyError("undefined url or path")
        curr: EndPoints = Constant.Current_Acc.get()
        for i in Constant.Accounts:
            i: ExtraAuth
            if i.username == self.name.get():
                img_pil.save(os.path.join(save_path, f"{i.user_id}.ico"),format='ICO')
        size = (30, 30)
        self.avt_img = CTkImage(img_pil, size=size if (size[0] != 0 or size[1] != 0) else img_pil.size)
        self._size_update(self['height'])
        self.label_avt.configure(image=self.avt_img)

    def set_avt(self, url=URL_PLYER_CARD_DEF, path=None):
        self.winfo_toplevel().loop.create_task(self._set_avt(url, path))

    def set_name(self, name: str):
        self.name.set(name)

    def set_title(self, text: str):
        self.title.set(text)

    def set_status(self, text):
        self.acc_status.set_status(text)


class AddAcc(CTkFrame):
    def __init__(self, master, corner_radius, command=None, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)
        # init frame
        self.configure(fg_color=self._detect_color_of_master())
        self.configure(bg_color=self.winfo_toplevel()["background"])

        img = CTkImage(load_img("./assets/img/add-d.png"), load_img("./assets/img/add-l.png"), size=(40, 40))
        button = CTkButton(self, text='', image=img, fg_color="transparent", hover=False)
        if command is not None:
            button.configure(command=command)
        button.place(relx=.5, rely=.5, anchor=CENTER, relheight=1)


class AccInfor(CTkFrame):
    def __init__(self, master, corner_radius, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)

        # init frame
        self.height = self.master["height"]
        self.corner_radius = corner_radius
        self.loop: AbstractEventLoop = self.winfo_toplevel().loop
        self.configure(height=self.height)

        # setup value
        self.values = []
        self.frames = []
        self.callbacks = []
        self.shift_index = 0
        self.target_index = 0

        # init image
        img_up = CTkImage(load_img("./assets/img/arrow-up-d.png"), load_img("./assets/img/arrow-up-l.png"))
        img_down = CTkImage(load_img("./assets/img/arrow-down-d.png"), load_img("./assets/img/arrow-down-l.png"))

        # button change Acc
        self.button_frame = CTkFrame(self, fg_color="transparent", height=self.height, width=40)

        buttons_up = CTkButton(self.button_frame, text='', width=40, command=self.up,
                               fg_color="transparent", hover=False, image=img_up)

        buttons_down = CTkButton(self.button_frame, text='', width=40, command=self.down,
                                 fg_color="transparent", hover=False, image=img_down)

        buttons_up.pack(side=TOP, fill=BOTH, expand=True)
        buttons_down.pack(side=TOP, fill=BOTH, expand=True)
        self.button_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        # button add Acc
        self.button_Acc = AddAcc(self, command=self.handel_click, corner_radius=20)


    def handel_click(self):
        self.winfo_toplevel().render_("login")

    async def update_pos_widget(self):

        if self.target_index > self.shift_index:
            step = range(self.shift_index, self.target_index, 2)
        else:
            step = range(self.shift_index, self.target_index, -2)

        for i in step:
            self.shift_index = i
            self.render_acc()
            await asyncio.sleep(0.015)

        self.shift_index = self.target_index

    def render_acc(self):
        for index, ele in enumerate(self.frames):
            ele.place(x=0, y=index * self.height - self.shift_index, relheight=1, relwidth=1)

        self.button_Acc.place(x=0, y=len(self.frames) * self.height - self.shift_index, relwidth=1, relheight=1)

        self.button_frame.lift()

    def _render_frame(self, data: dict):
        logger.info(data)
        frame = Acc(self, 20, height=self.height)
        frame.set_avt(data.get('avt', ''))
        frame.set_name(data.get('name', ''))
        frame.set_title(data.get('title', ''))
        self.frames.append(frame)

    def add(self, name: str, title: str, avt: str):
        data = {
            "name": name,
            "avt": avt,
            "title": title
        }
        for i in self.values:
            if name == i['name']:
                return
        self.values.append(data)
        self._render_frame(data)

        self.render_acc()

    def set_status_current_account(self, text):
        index = self.target_index // self.height
        if len(self.frames) <= index:
            return
        frame = self.frames[index]
        frame.set_status(text)

    def up(self):
        if self.target_index - self.height < 0:
            return

        self.target_index -= self.height

        self.loop.create_task(self.update_pos_widget())

        self._call_callback(self.target_index // self.height)


    def down(self):
        if self.target_index + self.height > len(self.frames) * self.height:
            return

        self.target_index += self.height

        self.loop.create_task(self.update_pos_widget())

        self._call_callback(self.target_index // self.height)

    def is_account_change(self, callback):
        self.callbacks.append(callback)

    def _call_callback(self, *args):
        for i in self.callbacks:
            if inspect.iscoroutinefunction(i):
                self.loop.create_task(i(*args))
            else:
                i(*args)
