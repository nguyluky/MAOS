import tkinter
import logging
import asyncio
import inspect

from CTkMessagebox import CTkMessagebox
from ValLib import User
from widgets.Loading import *
from Constant import Constant
from ValLib import authenticate, EndPoints, exceptions
from widgets.Structs import BaseMainFrame
from widgets.ImageHandel import load_img

logger = logging.getLogger("main_app")


async def handel_add_cookie(user: User):
    try:
        auth = await authenticate(user)
        Constant.Accounts.append(auth)
        Constant.EndPoints.append(EndPoints(auth))
        return True

    except exceptions.AuthException as err:
        CTkMessagebox(title="Error", message=err)
        return False


class Login(BaseMainFrame):
    def __init__(self, master, close_click, *arg, **kw):
        super().__init__(master, *arg, **kw)
        # init value
        self.loop = asyncio.get_event_loop()
        self.loading_ = Loaing(self, text="Loading",
                               height=80, width=90, type_=ICON)
        self.login_text_font = CTkFont("VALORANT", 40)
        self.fill_font = CTkFont("MarkPro-Medium", 14)

        self.check_var = tkinter.BooleanVar(self, False)
        self.callbacks = []

        self.user_pass_fill = None
        self.user_name_fill = None

        # button close
        close_img = CTkImage(load_img(r'assets\img\close-d.png'),
                             load_img(f'assets\img\close-l.png'))
        self.close_button = CTkButton(
            self, image=close_img, command=close_click, text='', fg_color="transparent", height=40, width=40)

        # layout
        self.frame_center = CTkFrame(self)
        self.frame_center.place(anchor="c", relx=.5,
                                rely=.5, relwidth=0.6, relheight=0.7)
        login_text = CTkLabel(
            self.frame_center, text="login", font=self.login_text_font)
        login_text.pack(pady=(20, 0))

        self.frame_user_name_pass_fill = CTkFrame(
            self.frame_center, fg_color="transparent")

        self._render_user_pass()

        self.frame_user_name_pass_fill.pack(fill=X, side=TOP, expand=True)

        def button_command():
            logger.debug('button login')
            self.frame_center.place_forget()
            self.loading_.place(anchor="c", relx=.5, rely=.5,
                                relwidth=0.6, relheight=0.7)
            self.login(self.user_name_fill.get(),
                       self.user_pass_fill.get(), self.check_var.get())

        self.button = CTkButton(
            self.frame_center, text="LOGIN", height=35, command=button_command)
        self.button.pack(side=BOTTOM, pady=(0, 20))

    def _render_user_pass(self):
        if self.user_name_fill:
            self.user_name_fill.destroy()
            
        # TODO
        self.user_name_fill = CTkEntry(
            self.frame_user_name_pass_fill, placeholder_text="USERNAME", height=35, width=250, font=self.fill_font)
        self.user_name_fill.place(relx=.5, rely=.20, anchor='c')

        if self.user_pass_fill:
            self.user_pass_fill.destroy()
        self.user_pass_fill = CTkEntry(
            self.frame_user_name_pass_fill, placeholder_text="PASSWORD", height=35, width=250, font=self.fill_font)
        self.user_pass_fill.place(relx=.5, rely=.60, anchor='c')

        checkbox = CTkCheckBox(self.frame_user_name_pass_fill, text="remember", variable=self.check_var, onvalue=True,
                               offvalue=False)
        checkbox.place(relx=.5, rely=.85, anchor='c')

    async def _login(self, user_name, passw, remember):
        logger.debug('start login')
        logger.debug('login at {} {} {}'.format(user_name, passw, remember))
        user = User(user_name, passw, remember)
        a = await handel_add_cookie(user)
        if not a:
            self.loading_.hidden()
            self.frame_center.place(
                anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)
        else:
            self.call_callback()

    def login(self, user_name, passw, remember):
        self.loop.create_task(self._login(user_name, passw, remember))

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callback(self):
        for i in self.callbacks:
            if inspect.iscoroutinefunction(i):
                self.loop.create_task(i())
            else:
                i()

    def show(self):
        super().show()

        self._render_user_pass()
        self.check_var.set(False)
        if len(Constant.Accounts) != 0:
            self.close_button.place(relx=1, y=0, anchor=NE)
