import asyncio
import logging
import ctypes
import json
import pickle
import tkinter.font

from win32com.client import Dispatch
from ctypes import windll
from CTkMessagebox import CTkMessagebox
from customtkinter import *
from CTkToolTip import CTkToolTip
from ValLib import async_login_cookie, ExtraAuth, exceptions, authenticate, EndPoints, User
from asyncio.events import AbstractEventLoop

from Constant import Constant
from widgets.Home import Home, star_game, set_to_backup_setting, get_player_card
from widgets.Loading import Loaing, PROGRESS
from widgets.Login import Login

run = True
icon_path = r".\icons\icon.ico"
if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS, icon_path)
else:
    icon_path = icon_path


CORNER_RADIUS = 20

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

logger = logging.getLogger("main_app")
logger.setLevel(logging.DEBUG)
logging.basicConfig(format="%(asctime)s [%(filename)-15.15s] [%(funcName)-15.15s] [%(levelname)-5.5s]  %(message)s")

try:
    os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS'))
except FileExistsError:
    pass
try:
    os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS\\Avt'))
except FileExistsError:
    pass

file_cookie = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\data.d")
game_setting = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting_global.json")
app_setting = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting.json")

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
        self.window = App((810, 450), "MAOS", icon_path, loop)
        await self.window.show()

def create_shortcut():
    logger.debug('craft shortcut')
    desktopFolder = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
    if getattr(sys, 'frozen', False):
        scriptsDir = os.path.dirname(sys._MEIPASS)
    else:
        scriptsDir = os.path.dirname(__file__)
    
    shell = Dispatch('WScript.Shell')
    for i in Constant.Accounts:
        i: ExtraAuth
        
        if i.username == '': continue
        
        
        pathLink = os.path.join(desktopFolder, f"{i.username}.lnk")
        shortcut = shell.CreateShortCut(pathLink)
        
        # command
        if getattr(sys, 'frozen', False):
            targer = os.path.join(os.path.dirname(sys._MEIPASS), './MAOS.exe')
            shortcut.Targetpath = targer
            shortcut.Arguments = f'-login={i.user_id}'
        else:
            targer = f"{sys.executable}"
            shortcut.Targetpath = targer
            shortcut.Arguments = f'{__file__} -login={i.user_id}'
            
        # icon
        shortcut.IconLocation = os.path.join(os.getenv('LOCALAPPDATA'), fr'MAOS\Avt\{i.user_id}.ico')
        shortcut.save()

async def load_cookie_file(progress=None):
    try:
        with open(file_cookie, 'rb+') as file:
            data = pickle.load(file)
            for i in data:
                logger.debug(i.user_id)
            logger.debug(f'load {len(data)} account')
            
            await load_cookie(data, progress)
    except FileNotFoundError as err:
        logger.warning(F'fail load cookie: {err}')

async def load_cookie(auths: ExtraAuth, progress):
        len_ = len(auths)
        if len_ == 0:
            return

        class HandelCookie:
            def __init__(self, progress):
                self.count = 0
                self.loading_startup = progress

            async def login_cookie(self, auth: ExtraAuth):
                auth = await async_login_cookie(auth)
                logger.debug(f'start login to {auth.username}')
                self.count += 1
                if self.loading_startup:
                    self.loading_startup.setprogress(self.count / len_)
                return auth

        loading = HandelCookie(progress)

        tasks = [loop.create_task(loading.login_cookie(i)) for i in auths]
        Constant.Accounts = await asyncio.gather(*tasks)
        for i in Constant.Accounts:
            Constant.EndPoints.append(EndPoints(i))

def load_valorant_setting():
    try:
        with open(game_setting, 'r+', encoding='UTF-8') as file:
            Constant.Setting_Valorant = json.loads(file.read())
    except (FileNotFoundError, json.JSONDecodeError):
        Constant.Setting_Valorant = {}
        
    # logger.info(Constant.Current_Acc_Setting)

def add_font_file(file):
    
    if getattr(sys, 'frozen', False):
        file = os.path.join(sys._MEIPASS, file)
    else:
        file = file
    
    fr_private = 0x10

    file = ctypes.byref(ctypes.create_unicode_buffer(file))
    font_count = windll.gdi32.AddFontResourceExW(file, fr_private, 0)

    if font_count == 0:
        raise RuntimeError("Error while loading font.")

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
    
    if len(sys.argv) > 1:
        for i in sys.argv:
            if '-login' in i:
                uuid = i.replace('-login=', '')
                logger.debug(f'login at {uuid}')
                loop.run_until_complete(run_without_gui(uuid))
                # loop.run_until_complete(test())
        
    else:
        add_font_file(".\\fonts\\Valorant Font.ttf")
        add_font_file("./fonts/FontFont_FF.Mark.Pro.Medium.otf")
        loop.run_until_complete(MainApp().exec(loop))
