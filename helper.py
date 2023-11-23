import logging
import os
import sys
import pickle
import asyncio
import json
import ctypes
import httpx

from ctypes import windll
from win32com.client import Dispatch


from ValLib import ExtraAuth, async_login_cookie, EndPoints
from Constant import Constant


logger = logging.getLogger("main_app")
logger.setLevel(logging.DEBUG)
logging.basicConfig(format="%(asctime)s [%(filename)-15.15s] [%(funcName)-15.15s] [%(levelname)-5.5s]  %(message)s")

file_cookie = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\data.d")
game_setting = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting_global.json")
app_setting = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting.json")

def create_shortcut():
    logger.debug('craft shortcut')
    desktopFolder = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
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
        
        loop = asyncio.get_event_loop()
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
        
    file = get_path(file)
    
    fr_private = 0x10

    file = ctypes.byref(ctypes.create_unicode_buffer(file))
    font_count = windll.gdi32.AddFontResourceExW(file, fr_private, 0)

    if font_count == 0:
        raise RuntimeError("Error while loading font.")


def get_path(path):
    if getattr(sys, 'frozen', False):
        path = os.path.join(sys._MEIPASS, path)
    else:
        path = path
        
    return path

def make_dir():
    try:
        os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS'))
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS\\Avt'))
    except FileExistsError:
        pass

async def check_account_status(account: EndPoints):
    party_infor = await account.Party.async_Party_Player()
    if party_infor.get("httpStatus", False):
        return "off"
        # self.acc_infor.set_status_current_account("off")
    else:
        current_game = await account.CurrentGame.async_Current_Game()
        match_id = current_game.get("MatchID", False)
        if match_id:
            return "in"
            # self.acc_infor.set_status_current_account("in")
        else:
            return "on"
            # self.acc_infor.set_status_current_account("on")

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

async def get_acc_infor(pvp: EndPoints):
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
    
    return account.username, avt, title
