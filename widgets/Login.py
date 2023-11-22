import tkinter
import logging
import asyncio
import inspect

from ValLib import User
from widgets.Loading import *
from Constant import Constant
from ValLib import authenticate, EndPoints, exceptions
from CTkMessagebox import CTkMessagebox


logger = logging.getLogger("main_app")

async def handel_add_cookie(user: User):
    try:  
        auth = await authenticate(user)
        Constant.Accounts.append(auth)
        Constant.EndPoints.append(EndPoints(auth))
        return True

    except exceptions.AuthException as err:
        CTkMessagebox(type="Error", message=err)
        return False


class Login(CTkFrame):
    def __init__(self, master, *arg, **kw):
        super().__init__(master, *arg, **kw)
        self.loop = asyncio.get_event_loop()
        self.logger = Loaing(self, text="Loading", height=80, width=90, type_=ICON)
        
        # init value
        login_text_font = CTkFont("VALORANT", 40)
        check_var = tkinter.BooleanVar(self, False)
        fill_font = CTkFont("MarkPro-Medium", 14)
        self.callbacks = []

        # layout
        self.frame = CTkFrame(self)
        self.frame.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)
        
        login_text = CTkLabel(self.frame, text="login", font=login_text_font)
        login_text.pack(pady=(20, 0))


        frame_user_name_pass_fill = CTkFrame(self.frame, fg_color="transparent")
        user_name_fill = CTkEntry(frame_user_name_pass_fill, placeholder_text="USERNAME", height=35, width=250,
                                  font=fill_font)
        user_name_fill.place(relx=.5, rely=.20, anchor='c')

        user_pass_fill = CTkEntry(frame_user_name_pass_fill, placeholder_text="PASSWORD", height=35, width=250,
                                  font=fill_font)
        user_pass_fill.place(relx=.5, rely=.60, anchor='c')

        checkbox = CTkCheckBox(frame_user_name_pass_fill, text="remember", variable=check_var, onvalue=True,
                               offvalue=False)
        checkbox.place(relx=.5, rely=.85, anchor='c')

        frame_user_name_pass_fill.pack(fill=X, side=TOP, expand=True)

        def button_command():
            logger.debug('button login')
            self.frame.place_forget()
            self.logger.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)
            self.login(user_name_fill.get(), user_pass_fill.get(), check_var.get())

        button = CTkButton(self.frame, text="LOGIN", height=35, command=button_command)
        button.pack(side=BOTTOM, pady=(0, 20))

    async def _login(self, user_name, passw, remember):
        logger.debug('start login')
        logger.debug('login at {} {} {}'.format(user_name, passw, remember))
        user = User(user_name, passw, remember)
        a = await handel_add_cookie(user)
        if not a:
            self.logger.place_forget()
            self.frame.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)
        
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