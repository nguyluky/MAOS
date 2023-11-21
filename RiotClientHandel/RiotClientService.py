from .Helper import *
from ValLib import Auth
from .ClientPrivate import ClientPrivate


import yaml
import psutil



class RiotClientService:
    def __init__(self):
        pass

    @staticmethod
    def kill_RiotClientServices():
        for proc in psutil.process_iter():
            name = proc.name()
            if "RiotClientServices" in name:
                proc.kill()

    @staticmethod
    def CreateAuthenticationFile(user: Auth):
        p_settings_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games', 'Riot Client', 'Data',
                                       'RiotGamesPrivateSettings.yaml')
        p_settings_path_backup = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games', 'Riot Client', 'Data',
                                              'RiotClientPrivateSettings.yaml')
        p_client_settings_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games', 'Riot Client', 'Config',
                                              'RiotClientSettings.yaml')

        riot_client = find_riot_client()
        file_infor = get_file_version_info(riot_client)
        client_setting = ClientPrivate(user)
        if int(file_infor[0]) >= 46:
            with open(p_client_settings_path, 'w+') as file:
                data = client_setting.CreateSettingsModel()
                file.write(data)

            with open(p_settings_path, "w+") as file:
                data = client_setting.CreateGameModelWRegion()
                file.write(data)

        else:
            with open(p_settings_path, 'w+') as file:
                data = client_setting.CreateGameModel()
                file.write(data)

            with open(p_settings_path_backup, "w+") as file:
                data = client_setting.CreateClientPrivateModel()
                file.write(data)

    @staticmethod
    async def OnValorantGameLaunched():
        pass

