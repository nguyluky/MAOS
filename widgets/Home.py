import subprocess
import logging

from threading import Thread
from asyncio.events import AbstractEventLoop
from Constant import Constant
from RiotClientHandel import RiotClientService, find_riot_client
from ValLib import EndPoints
from widgets.AccInfor import *
from widgets.TabView import *
from widgets.Timer_async import SetInterval, SetTimeout

CORNER_RADIUS = 20

logger = logging.getLogger("main_app")

async def get_player_card(player_card_id) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://valorant-api.com/v1/playercards/{player_card_id}")
        data = resp.json()
        return data["data"]["smallArt"]

async def get_player_name(pvp: EndPoints) -> str:
    name_data = await pvp.Pvp.async_Name_Service()
    name_data = dict(name_data[0])
    GameName = name_data.get('GameName', '')
    TagLine = name_data.get('TagLine', '')
    if GameName != '' and TagLine != '':
        return f"{GameName}#{TagLine}"
    return ''


async def get_player_titles(player_title_id):
    if player_title_id == "00000000-0000-0000-0000-000000000000":
        return ""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://valorant-api.com/v1/playertitles/{player_title_id}")
        data = resp.json()
        try:
            titles = data["data"]["titleText"]
            return titles
        except KeyError:
            return ''

async def star_game(callback):

    RiotClientService.kill_RiotClientServices()
    await asyncio.sleep(1)
    # copy setting
    endpoint: EndPoints = Constant.Current_Acc.get()
    
    if Constant.App_Setting.get()['Change settting game before play']:
        current_acc_setting = await endpoint.Setting.async_Fetch_Preference()
        Constant.Current_Acc_Setting = current_acc_setting

        # set global setting
        await endpoint.Setting.async_Put_Preference(Constant.Setting_Valorant)

    # start game
    path = find_riot_client()
    RiotClientService.CreateAuthenticationFile(endpoint.auth)

    logger.debug('start game')
    command = f"{path} --launch-product=valorant --launch-patchline=live --insecure --launch-product=valorant"
    loop = asyncio.get_event_loop()
    thread = Thread(target=_star_game_thread, args=(command,callback,loop ))
    thread.start()
    
def _star_game_thread(command, callback, loop):
    ls_output = subprocess.Popen(command)
    ls_output.communicate()
    loop.create_task(callback())
    
async def set_to_backup_setting():
    logger.debug('game quit')
    RiotClientService.kill_RiotClientServices()
    # set current setting
    logger.debug("setback to before setting")
    await asyncio.sleep(1)
    endpoint: EndPoints = Constant.Current_Acc.get()
    if Constant.App_Setting.get()['Change settting game before play']:
        await endpoint.Setting.async_Put_Preference(Constant.Current_Acc_Setting)

class Home(CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # init value
        Constant.Current_Acc.set(Constant.EndPoints[0])
        self.loop: AbstractEventLoop = self.winfo_toplevel().loop
        self.check_account_status_timer = SetInterval(Constant.App_Setting.get()['refresh time'], self.check_account_status)
        Constant.App_Setting.add_callback(self.setting_change)
        
        #
        self.main_home_frame = CTkFrame(self, fg_color="transparent")

        home_frame_top = CTkFrame(self.main_home_frame, height=80, fg_color="transparent")
        home_frame_top.pack(side=TOP, fill=X)

        home_frame_top.grid_columnconfigure(0, weight=7)
        home_frame_top.grid_columnconfigure(1, weight=1)

        # AccInfor
        self.acc_infor = AccInfor(home_frame_top, corner_radius=CORNER_RADIUS)
        self.acc_infor.grid(row=0, column=0, sticky=NSEW, padx=(10, 0), pady=10)
        self.acc_infor.is_account_change(self.handel_event)

        # play button
        button_play_font = CTkFont("Consolas", 20, "bold")
        button_play = CTkButton(home_frame_top, text="PLAY", width=50, font=button_play_font,
                                command=lambda: self.loop.create_task(self.handel_play_button()))
        button_play.grid(row=0, column=1, sticky=NSEW, padx=(20, 10), pady=30)

        # tabView - shop -
        home_frame_button = TabView(self.main_home_frame, corner_radius=CORNER_RADIUS)
        home_frame_button.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.main_home_frame.pack(fill=BOTH, expand=True)

    async def setting_change(self, mode, value):
        logger.debug('change refresh time')
        if self.check_account_status_timer:
            self.check_account_status_timer.cancel()
        self.check_account_status_timer = SetInterval(Constant.App_Setting.get()['refresh time'], self.check_account_status)

    async def handel_play_button(self):
        logger.debug('play button clicked')
        await star_game(self.game_quit)
        self.winfo_toplevel().withdraw()

    async def game_quit(self):
        await set_to_backup_setting()
        self.winfo_toplevel().deiconify()

    def handel_event(self, index):
        if index < len(Constant.EndPoints):
            Constant.Current_Acc.set(Constant.EndPoints[index])
            SetTimeout(1, self.check_account_status)

    async def api_star(self):
        for pvp in Constant.EndPoints:
            await self.render_acc_infor(pvp)

    async def render_acc_infor(self, pvp: EndPoints):

        # find index of auth in account list
        index = -1
        for i, ele in enumerate(Constant.Accounts):
            if ele == pvp.auth:
                index = i
                break

        data = await pvp.Pvp.async_Player_Loadout()
        if pvp.auth.username == '':
            name = await get_player_name(pvp)
            Constant.Accounts[index].username = name

        if pvp.auth.card_id == '':
            player_card_id = data.identity.player_card_id
            Constant.Accounts[index].card_id = player_card_id

        if pvp.auth.title_id == '':
            player_title_id = data.identity.player_title_id
            Constant.Accounts[index].title_id = player_title_id

        account = Constant.Accounts[index]

        avt = await get_player_card(account.card_id)
        title = await get_player_titles(account.title_id)

        self.acc_infor.add(account.username, title, avt)

    def show(self):
        self.place(x=0, y=0, relwidth=1, relheight=1)
        task = self.loop.create_task(self.api_star())
        task.add_done_callback(lambda x: self.check_account_status_timer.star())

    def place_forget(self):
        super().place_forget()
        self.check_account_status_timer.cancel()

    async def check_account_status(self):
        account: EndPoints = Constant.Current_Acc.get()

        party_infor = await account.Party.async_Party_Player()
        if party_infor.get("httpStatus", False):
            self.acc_infor.set_status_current_account("off")
        else:
            current_game = await account.CurrentGame.async_Current_Game()
            match_id = current_game.get("MatchID", False)
            if match_id:
                self.acc_infor.set_status_current_account("in")
            else:
                self.acc_infor.set_status_current_account("on")
