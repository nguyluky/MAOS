import os
import sys
import ctypes
import json
import logging

from win32api import *

logger = logging.getLogger("main_app")

def find_riot_client():
    clients = []

    riot_install_path = os.path.join(os.getenv('ProgramData'), 'Riot Games', 'RiotClientInstalls.json')

    if not os.path.exists(riot_install_path):
        return None

    try:
        with open(riot_install_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError as e:
        logger.warning("Riot Client Check: Could not properly parse json file")
        return None

    for client_type in ['rc_live', 'rc_beta', 'rc_esports', 'rc_default']:
        if client_type in config and isinstance(config[client_type], str):
            clients.append(config[client_type])

    for client_path in clients:
        if os.path.exists(client_path):
            return client_path

    return None


def get_file_version_info(file_path):
    File_information = GetFileVersionInfo(file_path, "\\")

    ms_file_version = File_information['FileVersionMS']
    ls_file_version = File_information['FileVersionLS']

    return [str(HIWORD(ms_file_version)), str(LOWORD(ms_file_version)),
            str(HIWORD(ls_file_version)), str(LOWORD(ls_file_version))]
