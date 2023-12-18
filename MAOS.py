import subprocess

from CTkMessagebox import CTkMessagebox
from customtkinter import *
from asyncio.events import AbstractEventLoop
from pystray import Icon, Menu, MenuItem

from Helper.helper import *
from Helper.Constant import Constant
from Widgets.Login import Login
from Widgets.AccountSwitch import AccountSwitch
from Widgets.Home import Home, star_game, set_to_backup_setting, is_game_run
from Widgets.Loading import Loading, PROGRESS
from Widgets.ImageHandel import load_img

run = True
CORNER_RADIUS = 20
VERSION = "1.0.4"

logger = logging.getLogger("main_app")


class App(CTk):
    def __init__(self, start_size, title, icon, loop_: AbstractEventLoop) -> None:
        super().__init__()

        # load app setting
        logger.debug("load app setting")
        load_app_setting(self)

        # load valorant setting
        logger.debug("load valorant setting")
        load_valorant_setting()

        # init window
        self.title(title)
        self.geometry(f"{start_size[0]}x{start_size[1]}")
        self.iconbitmap(icon)
        set_appearance_mode("Dark")
        set_default_color_theme("blue")

        # icon_tray
        self.icon_tray = Icon("MAOS", load_img(r'assets\icons\icon.ico'), "MAOS", Menu(
            MenuItem("Show", lambda icon_, item: self.loop.create_task(self.show_window())),
            MenuItem("Set game default setting", lambda icon_, item: self.loop.create_task(self.show_window())),
            MenuItem("Quit", lambda icon_, item: self.loop.create_task(self.async_on_quit()))),
                              )
        self.icon_tray.run_detached()

        # init value
        self.isShow = True
        self.exitFlag = False
        self.loop = loop_
        self.new_version_url = None

        # main frame
        self.frames = {
            "home": Home(self, lambda: self.render_("account_change"), self.hide_window),
            "loading_stats": Loading(self, type_=PROGRESS, text=""),
            "login": Login(self, corner_radius=CORNER_RADIUS, close_click=self.handel_button_login_close),
            "account_change": AccountSwitch(self, corner_radius=CORNER_RADIUS,
                                            close_click=self.handel_button_login_close,
                                            add_click=self.handel_button_login_add)
        }
        self.frames['login'].add_callback(self.handel_button_login_close)

        # check update and load cookie
        task = self.loop.create_task(self.check_before_run())
        task.add_done_callback(lambda *args: self.widget_update())

        # add event
        self.protocol("WM_DELETE_WINDOW", self.quit_handel)

    async def check_before_run(self):
        loading_stats = self.frames['loading_stats']
        loading_stats.show()

        loading_stats.set_text("check update")
        await self.check_update()

        loading_stats.set_text("loading cookie")
        logger.debug('load cookie')
        await load_cookie_file(loading_stats)

        if Constant.App_Setting.default_account.get() == "":
            return

        for endpoint in Constant.EndPoints:
            if endpoint.auth.username == Constant.App_Setting.default_account.get():
                Constant.Current_Acc.set(endpoint)

    async def check_update(self):
        url_file = await check_update()
        if url_file is None:
            return

        # if not getattr(sys, 'frozen', False):
        #     logger.debug(f"new update {url_file}")
        #     return True

        msg = CTkMessagebox(title="Software Update", message="MASO 1.0.4 are releases \n Do you want update",
                            icon="question", option_1="Update now", option_2="Update when exit", option_3="No")
        response = msg.get()
        logger.debug(response)
        if response == "Yes":
            pass

    async def async_on_quit(self):
        self.on_quit()

    async def show_window(self):
        self.deiconify()
        self.isShow = True

    def handel_button_login_add(self):
        self.render_('login')

    def handel_button_login_close(self, *args):
        logger.debug(f"handel login args {args}")
        self.render_('home')

    def widget_update(self, *args):
        logger.debug(f"widget update args {args}")
        self.clear_()
        if len(Constant.Accounts) == 0:
            self.render_("login")
        else:
            self.render_("home")

    def clear_(self):
        for frame in self.frames.values():
            frame.hidden()

    def render_(self, win=None):
        self.clear_()
        if win is None:
            return

        frame = self.frames[win]
        frame.show()

    def hide_window(self):
        self.withdraw()
        self.isShow = False
        logger.debug('hide main window')

    def quit_handel(self):
        if Constant.App_Setting.run_on_background.get():
            self.hide_window()
            return
        self.on_quit()

    def on_quit(self, *args, is_save=True):
        logger.debug(f'quit with args {args}')
        self.exitFlag = True

        if is_save:
            self.save_config()

        self.update()
        self.icon_tray.stop()
        # self.withdraw()

    @staticmethod
    def save_config():
        accounts = []
        # save account
        for account in Constant.Accounts:
            if account.remember:
                accounts.append(account)
        with open(COOKIE_PATH, "wb+") as file:
            pickle.dump(accounts, file)

        # game setting
        with open(GAME_SETTING_PATH, 'w+', encoding='UTF-8') as file:
            setting = json.dumps(Constant.Setting_Valorant)
            file.write(setting)

        with open(APP_SETTING_PATH, 'w+') as file:
            setting = json.dumps(Constant.App_Setting.to_dict())
            file.write(setting)

        if Constant.App_Setting.craft_shortcut.get():
            create_shortcut()

    async def main_loop(self):
        self.update()
        await asyncio.sleep(.01)

    async def client_update(self):
        if not Constant.App_Setting.backup_setting.get():
            self.on_quit()
            return

        if not await is_game_run():
            Constant.Is_Game_Run = False
            self.deiconify()
            self.isShow = True
            self.focus()
            await set_to_backup_setting()
        await asyncio.sleep(2)

    async def show(self):
        while not self.exitFlag:
            if Constant.Is_Game_Run:
                await self.client_update()
            elif not self.isShow:
                await asyncio.sleep(1)
            else:
                await self.main_loop()

        self.quit()
        logger.debug('app exit')


class MainApp:
    def __init__(self):
        self.window = None

    async def exec(self, loop_):
        icon_path = get_path(r".\assets\icons\icon.ico")
        self.window = App((810, 450), "MAOS", icon_path, loop_)
        await self.window.show()


async def check_update():
    async with httpx.AsyncClient() as client:
        data = await client.get("https://api.github.com/repos/nguyluky/MAOS/releases")
        last_release = data.json()[0]

        tag = last_release["tag_name"]

        if tag < VERSION:
            logger.info("no update")
            return None

        logger.info(f"new update {tag}")
        assets = last_release["assets"]
        url_file = None
        for asset in assets:
            if asset["name"] == "MAOS.zip":
                url_file = asset["browser_download_url"]

        return url_file


async def run_without_gui(player_uuid):
    await load_cookie_file()
    for account in Constant.Accounts:
        if account.user_id == player_uuid:
            Constant.Current_Acc.set(EndPoints(account))

    load_valorant_setting()
    # load_app_setting(None)

    curr_acc = Constant.Current_Acc.get()
    if curr_acc is None:
        return

    setting: dict = {}
    with open(APP_SETTING_PATH) as file:
        setting = json.loads(file.read())

    await star_game(setting.get("overwrite_setting", False))
    await asyncio.sleep(20)


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
