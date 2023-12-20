import subprocess
import psutil

from asyncio.events import AbstractEventLoop
from RiotClient import RiotClientService, find_riot_client
from Component.Widgets.AccInfor import *
from Component.Widgets.TabView import *
from Component.Structs import BaseMainFrame

CORNER_RADIUS = 20

logger = logging.getLogger("main_app")


async def is_game_run():
    for process in psutil.process_iter():
        name = process.name()
        if "RiotClientServices" in name:
            return True
    return False


async def star_game(overwrite_setting):
    RiotClientService.kill_RiotClientServices()
    await asyncio.sleep(1)
    # copy setting
    endpoint: EndPoints = Constant.Current_Acc.get()

    if overwrite_setting:
        logger.debug('overwrite game setting')
        current_acc_setting = await endpoint.Setting.async_Fetch_Preference()
        Constant.Current_Acc_Setting = current_acc_setting

        # set global setting
        await endpoint.Setting.async_Put_Preference(Constant.Setting_Valorant)

    # start game
    path = find_riot_client()
    RiotClientService.CreateAuthenticationFile(endpoint.auth)

    logger.debug('start game')
    command = f"{path} --launch-product=valorant --launch-patchline=live --insecure"
    subprocess.Popen(command)
    await asyncio.sleep(5)
    Constant.Is_Game_Run = True


async def set_to_backup_setting():
    logger.debug('game quit')
    RiotClientService.kill_RiotClientServices()
    # set current setting
    logger.debug("setback to before setting")
    await asyncio.sleep(1)
    endpoint: EndPoints = Constant.Current_Acc.get()
    await endpoint.Setting.async_Put_Preference(Constant.Current_Acc_Setting)


class Home(BaseMainFrame):
    def __init__(self, master, change_account_button_clicked=None, hide_main_window=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # init value
        self.loop: AbstractEventLoop = asyncio.get_event_loop()
        self.hide_main_window = hide_main_window

        #
        self.main_home_frame = CTkFrame(self, fg_color="transparent")

        home_frame_top = CTkFrame(
            self.main_home_frame, height=80, fg_color="transparent")
        home_frame_top.pack(side=TOP, fill=X)

        home_frame_top.grid_columnconfigure(0, weight=7)
        home_frame_top.grid_columnconfigure(1, weight=1)

        # AccInfo
        self.acc_info = AccInfor(home_frame_top, corner_radius=CORNER_RADIUS,
                                 change_account_click=change_account_button_clicked)
        self.acc_info.grid(row=0, column=0, sticky=NSEW,
                           padx=(10, 0), pady=(0, 10))

        # play button
        button_play_font = CTkFont("Consolas", 20, "bold")
        button_play = CTkButton(home_frame_top, text="PLAY", width=50, font=button_play_font,
                                command=lambda: self.loop.create_task(self.handel_play_button()))
        button_play.grid(row=0, column=1, sticky=NSEW, padx=(20, 10), pady=30)

        # tabView - shop -
        home_frame_button = TabView(
            self.main_home_frame, corner_radius=CORNER_RADIUS)
        home_frame_button.pack(side=TOP, fill=BOTH,
                               expand=True, padx=10, pady=(0, 10))
        self.main_home_frame.pack(fill=BOTH, expand=True)

    async def handel_play_button(self):
        logger.debug('play button clicked')
        self.hide_main_window()
        await star_game(Constant.App_Setting.overwrite_setting.get())

    def show(self):
        super().show()
        self.acc_info.update_account()
