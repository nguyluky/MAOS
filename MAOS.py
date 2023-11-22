import asyncio
import logging
import json
import pickle
import tkinter.font

from CTkMessagebox import CTkMessagebox
from customtkinter import *
from CTkToolTip import CTkToolTip
from ValLib import exceptions, authenticate, EndPoints, User
from asyncio.events import AbstractEventLoop

from Constant import Constant
from widgets.Home import Home, star_game, set_to_backup_setting
from widgets.Loading import Loaing, PROGRESS
from widgets.Login import Login
from helper import *

run = True
CORNER_RADIUS = 20

logger = logging.getLogger("main_app")

class App(CTk):
    def __init__(self, start_size, title, icon, loop: AbstractEventLoop) -> None:
        super().__init__()
        # init window
        self.title(title)
        self.geometry(f"{start_size[0]}x{start_size[1]}")
        self.iconbitmap(icon)
        set_appearance_mode("Dark")
        set_default_color_theme("blue")

        # tkinter.Variable
        self.index_user_curr = tkinter.IntVar(self, -1)
        # self.index_user_curr.trace("w", self.account_change)

        self.event_value_account_change = tkinter.BooleanVar(self, False)
        self.event_value_account_change.trace('w', self.widget_update)

        # init value
        self.loading_startup: Loaing = None
        self.login_frame_: Login = None
        self.main_home_frame: Home = None
        self.exitFlag = False
        self.loop = loop

        # loading cookie
        self.render_loading_startup()
        self.loading_startup.set_text("loading cookie file")
        
        
        # load cooki
        logger.debug('load data')
        task = self.loop.create_task(load_cookie_file(self.loading_startup))
        task.add_done_callback(lambda *args: self.widget_update())

        
        # loading valorant setting
        load_valorant_setting()
        
        # loading setting
        try:
            with open(app_setting, 'r+') as file:
                data = dict(json.loads(file.read()))
                new_setting = Constant.App_Setting.get()
                for key, value in data.items():
                    new_setting[key] = value
                Constant.App_Setting.set(new_setting)
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # add event
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    async def handel_add_cookie(self, user: User):
        try:
            
            auth = await authenticate(user)
            Constant.Accounts.append(auth)
            Constant.EndPoints.append(EndPoints(auth))
            self.render_("home")
            return True

        except exceptions.AuthException as err:
            CTkMessagebox(type="Error", message=err)
            return False

    def widget_update(self, *args):
        self.clear_()
        if len(Constant.Accounts) == 0:
            self.render_("login")
        else:
            self.render_("home")

    def clear_(self):
        for widgets in self.winfo_children():
            if isinstance(widgets, CTkToolTip):
                continue
            widgets.place_forget()
            widgets.pack_forget()

    def render_(self, win=None):
        self.clear_()
        if win is None:
            return

        if win == "login":
            self.render_login()

        elif win == "home":
            self.render_home()

        elif win == "loading":
            self.render_loading_startup()

    def render_home(self):
        if self.main_home_frame is None:
            self.main_home_frame = Home(self)
        self.main_home_frame.show()

    def render_login(self):
        self.login_frame_ = Login(self, fg_color="transparent", corner_radius=CORNER_RADIUS)
        self.login_frame_.place(x=0, y=0, relwidth=1, relheight=1)

    def render_loading_startup(self):
        self.loading_startup = Loaing(self, type_=PROGRESS, text="loading cookie")

        self.loading_startup.place(x=0, y=0, relwidth=1, relheight=1)

    def on_quit(self):
        logger.debug('quit')
        self.exitFlag = True
        accounts = []
        for i in Constant.Accounts:
            if i.remember:
                accounts.append(i)
        with open(file_cookie, "wb+") as file:
            pickle.dump(accounts, file)
        with open(game_setting, 'w+', encoding='UTF-8') as file:
            setting = json.dumps(Constant.Setting_Valorant)
            file.write(setting)
            
        with open(app_setting, 'w+') as file:
            setting = json.dumps(Constant.App_Setting.get())
            file.write(setting)    
        
        if Constant.App_Setting.get()['craft shortcut']:
            create_shortcut() 
        
        self.update()
        # self.withdraw()


    async def show(self):
        while not self.exitFlag:
            self.update()
            await asyncio.sleep(.01)

        self.quit()

class MainApp:
    def __init__(self):
        self.window = None

    async def exec(self, loop):
        icon_path = get_path(r".\assets\icons\icon.ico")
        self.window = App((810, 450), "MAOS", icon_path, loop)
        await self.window.show()

async def run_without_gui(uuid):
    await load_cookie_file()
    for i in Constant.Accounts:
        if i.user_id == uuid:
            Constant.Current_Acc.set(EndPoints(i))
    
    load_valorant_setting()
    
    curr_acc = Constant.Current_Acc.get()     
    if curr_acc is None:
        return
    
    await star_game(game_quit)
    while run:
        await asyncio.sleep(2)

async def game_quit():
    await set_to_backup_setting()
    global run
    run = False

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    make_dir()
    if len(sys.argv) > 1:
        for i in sys.argv:
            if '-login' in i:
                uuid = i.replace('-login=', '')
                logger.debug(f'login at {uuid}')
                loop.run_until_complete(run_without_gui(uuid))
                # loop.run_until_complete(test())
        
    else:
        add_font_file("./assets/fonts/Valorant Font.ttf")
        add_font_file("./assets/fonts/FontFont_FF.Mark.Pro.Medium.otf")
        loop.run_until_complete(MainApp().exec(loop))

a = set()