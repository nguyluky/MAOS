import asyncio
import logging
import json
import pickle
import tkinter.font

from customtkinter import *
from ValLib import EndPoints
from asyncio.events import AbstractEventLoop
from pystray import Icon, Menu, MenuItem

from helper import *
from Constant import Constant
from widgets.Login import Login
from widgets.AccountChange import AccountChange
from widgets.Home import Home, star_game, set_to_backup_setting, is_game_run
from widgets.Loading import Loaing, PROGRESS
from widgets.ImageHandel import load_img

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
        
        # icon_tray
        self.icon_tray = Icon("MAOS", load_img(r'assets\icons\icon.ico'), "MAOS", Menu(
            MenuItem("open", lambda icon, item: print(item)),
            MenuItem('heide', lambda icon, item: print(item)),
            MenuItem("heide tray", lambda icon, item: print(item)),
            MenuItem("exit", lambda icon, item: self.on_quit()),
        ))
        self.icon_tray.run_detached()

        self.event_value_account_change = tkinter.BooleanVar(self, False)
        self.event_value_account_change.trace('w', self.widget_update)

        # init value
        self.exitFlag = False
        self.loop = loop
        self.frames = {
            "home": Home(self, lambda: self.render_("account_change")),
            "loading_stats": Loaing(self, type_=PROGRESS, text="loading cookie"),
            "login": Login(self, corner_radius=CORNER_RADIUS, close_click=self.handel_button_login_close),
            "account_change": AccountChange(self, corner_radius=CORNER_RADIUS, close_click=self.handel_button_login_close, add_click=self.handel_button_login_add)
        }

        self.frames['login'].add_callback(self.handel_button_login_close)

        # loading cookie
        loading_stats = self.frames['loading_stats']
        loading_stats.show()
        loading_stats.set_text("loading cookie file")

        # load cooki
        logger.debug('load data')
        task = self.loop.create_task(load_cookie_file(loading_stats))
        task.add_done_callback(lambda *args: self.widget_update())

        # loading valorant setting
        load_valorant_setting()

        # loading setting
        try:
            with open(app_setting, 'r+') as file:
                data = dict(json.loads(file.read()))
                Constant.App_Setting.from_dict(data)

        except (FileNotFoundError, json.JSONDecodeError):
            pass

        # add event
        self.protocol("WM_DELETE_WINDOW", self.quit_handel)

    def quit_handel(self):
        if Constant.App_Setting["run-on-background"]:
            self.withdraw()
        self.on_quit()
    
    def handel_button_login_add(self):
        self.render_('login')

    def handel_button_login_close(self, *args):
        self.render_('home')

    def widget_update(self, *args):
        self.clear_()
        if len(Constant.Accounts) == 0:
            self.render_("login")
        else:
            self.render_("home")

    def clear_(self):
        for i in self.frames.values():
            i.hidden()

    def render_(self, win=None):
        self.clear_()
        if win is None:
            return

        fram = self.frames[win]
        fram.show()

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

        if Constant.App_Setting['craft-shortcut']:
            create_shortcut()

        self.update()
        self.icon_tray.stop()
        # self.withdraw()

    async def show(self):
        while not self.exitFlag:
            if not Constant.Is_Game_Run:
                self.update()
                await asyncio.sleep(.01)
            else:
                if not Constant.App_Setting["run-on-background"]:
                    await asyncio.sleep(10)
                    self.on_quit()
                    continue
                    
                if not await is_game_run():
                    Constant.Is_Game_Run = False
                    self.deiconify()
                    self.focus()
                    await set_to_backup_setting()
                await asyncio.sleep(2)
                
        self.quit()
        print("end")


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
