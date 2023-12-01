import logging
import os
import sys
import pickle
import asyncio
import json
import ctypes
import httpx
from datetime import date

from ctypes import windll
from win32com.client import Dispatch

from widgets.Variable import Setting
from ValLib import ExtraAuth, async_login_cookie, EndPoints
from Constant import Constant

# path init
COOKIE_PATH = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\data.d")
GAME_SETTING_PATH = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting_global.json")
APP_SETTING_PATH = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS\\setting.json")
PATH_SHORTCUT_START = os.path.join(os.getenv('APPDATA'), "Microsoft\\Windows\\Start Menu\\Programs\\MAOS")
PATH_SHORTCUT_HOME = os.path.join(os.path.expanduser('~'), 'Desktop')
MAOS = os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS')

# logging config
today = date.today()
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys._MEIPASS)
    logPath = os.path.join(base_path, "log")
else:
    logPath = "log"
logName = today.strftime("%d-%m-%Y")
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

logger = logging.getLogger("main_app")
logger.setLevel(logging.DEBUG)

if not os.path.exists(logPath):
    os.mkdir(logPath)

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, logName))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)


def _create_shortcut(path_shortcut, shell, endpoint: ExtraAuth):
    if endpoint.username == '':
        return

    path_link = os.path.join(path_shortcut, f"{endpoint.username}.lnk")
    shortcut = shell.CreateShortCut(path_link)

    # command
    if getattr(sys, 'frozen', False):
        target = os.path.join(os.path.dirname(sys._MEIPASS), './MAOS.exe')
        shortcut.Targetpath = target
        shortcut.Arguments = f'-login={endpoint.user_id}'
    else:
        target = f"{sys.executable}"
        shortcut.Targetpath = target
        shortcut.Arguments = f'{__file__} -login={endpoint.user_id}'

    # icon
    shortcut.IconLocation = os.path.join(
        os.getenv('LOCALAPPDATA'), fr'MAOS\Avt\{endpoint.user_id}.ico')
    shortcut.save()


def create_shortcut():
    logger.debug('craft shortcut')
    shell = Dispatch('WScript.Shell')
    for i in Constant.Accounts:
        if Constant.App_Setting['allows-desktop'].get():
            _create_shortcut(PATH_SHORTCUT_HOME, shell, i)

        if Constant.App_Setting['allows-start-menu'].get():
            _create_shortcut(PATH_SHORTCUT_START, shell, i)


async def load_cookie_file(progress=None):
    try:
        with open(COOKIE_PATH, 'rb+') as file:
            data = pickle.load(file)
            logger.debug(f'load {len(data)} account')

            await load_cookie(data, progress)
    except FileNotFoundError as err:
        logger.warning(F'fail load cookie: {err}')


async def load_cookie(auths: ExtraAuth, progress):
    len_ = len(auths)
    if len_ == 0:
        return

    class HandelCookie:
        def __init__(self, progress_):
            self.count = 0
            self.loading_startup = progress_

        async def login_cookie(self, auth: ExtraAuth):
            auth = await async_login_cookie(auth)
            logger.debug(f'start login to {auth.username}')
            self.count += 1
            if self.loading_startup:
                self.loading_startup.set_progress(self.count / len_)
            return auth

    loading = HandelCookie(progress)

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(loading.login_cookie(i)) for i in auths]
    Constant.Accounts = await asyncio.gather(*tasks)
    for i in Constant.Accounts:
        Constant.EndPoints.append(EndPoints(i))


def load_valorant_setting():
    logger.debug("loading valorant setting")
    try:
        with open(GAME_SETTING_PATH, 'r+', encoding='UTF-8') as file:
            Constant.Setting_Valorant = json.loads(file.read())
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("set default setting")
        Constant.Setting_Valorant = {}


def add_font_file(file):
    file = get_path(file)

    fr_private = 0x10

    file = ctypes.byref(ctypes.create_unicode_buffer(file))
    font_count = windll.gdi32.AddFontResourceExW(file, fr_private, 0)

    if font_count == 0:
        raise RuntimeError("Error while loading font.")


def get_path(path=None):
    if getattr(sys, 'frozen', False):
        path = os.path.join(sys._MEIPASS, path)
    else:
        path = path

    return path


def make_dir():
    avt = os.path.join(os.getenv('LOCALAPPDATA'), 'MAOS\\Avt')
    if not os.path.exists(MAOS):
        os.mkdir(MAOS)

    if not os.path.exists(avt):
        os.mkdir(avt)

    if not os.path.exists(PATH_SHORTCUT_START):
        os.mkdir(PATH_SHORTCUT_START)


async def check_account_status(account: EndPoints):
    party_info = await account.Party.async_Party_Player()

    if party_info.get("httpStatus", False):
        return "off"

    current_game = await account.CurrentGame.async_Current_Game()
    match_id = current_game.get("MatchID", False)
    if match_id:
        return "in"
    else:
        return "on"


async def get_player_card(player_card_id) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://valorant-api.com/v1/playercards/{player_card_id}")
        data = resp.json()
        return data["data"]["smallArt"]


async def get_player_name(pvp: EndPoints) -> str:
    name_data = await pvp.Pvp.async_Name_Service()
    name_data = dict(name_data[0])
    game_name = name_data.get('GameName', '')
    tag_line = name_data.get('TagLine', '')
    if game_name != '' and tag_line != '':
        return f"{game_name}#{tag_line}"
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


async def get_acc_info(pvp: EndPoints):
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


def load_app_setting(self):
    Constant.App_Setting = Setting(self)

    # loading setting
    logger.debug("loading setting")
    try:
        with open(APP_SETTING_PATH, 'r+') as file:
            data = dict(json.loads(file.read()))
            if data.get('version', None) is None:
                raise json.JSONDecodeError('wrong setting format', "", 0)
            Constant.App_Setting.from_dict(data)

    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning('No File Setting')
