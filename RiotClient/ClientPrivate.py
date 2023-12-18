from ValLib import Auth
import yaml
from dataclasses import dataclass


@dataclass
class CookieValue:
    tdid: str
    ssid: str
    clid: str
    sub: str
    csid: str


class ClientPrivate:

    def __init__(self, user: Auth):
        self.cookie_values = CookieValue('', '', '', '', '')

        for key, value in user.cookies.items():
            if key == "tdid":
                self.cookie_values.tdid = value
            elif key == "ssid":
                self.cookie_values.ssid = value
            elif key == "clid":
                self.cookie_values.clid = value
            elif key == "sub":
                self.cookie_values.sub = value
            elif key == "csid":
                self.cookie_values.csid = value

    def CreateGameModel(self):
        settings = {
            "riot-login": {
                "persist": {
                    "session": {
                        "cookies": [
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "tdid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": self.cookie_values.tdid
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "ssid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": self.cookie_values.ssid
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "clid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": "ue1"
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "sub",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": self.cookie_values.sub
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "csid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": self.cookie_values.csid
                            }
                        ]
                    }
                }
            }
        }

        return yaml.dump(settings)

    def CreateClientPrivateModel(self):
        settings = {
            "private": {
                "riot-login": {
                    "persist": {
                        "session": {
                            "cookies": [
                                {
                                    "domain": "auth.riotgames.com",
                                    "hostOnly": True,
                                    "httpOnly": True,
                                    "name": "tdid",
                                    "path": "/",
                                    "persistent": True,
                                    "secureOnly": True,
                                    "value": self.cookie_values.tdid
                                },
                                {
                                    "domain": "auth.riotgames.com",
                                    "hostOnly": True,
                                    "httpOnly": True,
                                    "name": "ssid",
                                    "path": "/",
                                    "persistent": True,
                                    "secureOnly": True,
                                    "value": self.cookie_values.ssid
                                },
                                {
                                    "domain": "auth.riotgames.com",
                                    "hostOnly": True,
                                    "httpOnly": True,
                                    "name": "clid",
                                    "path": "/",
                                    "persistent": True,
                                    "secureOnly": True,
                                    "value": "ue1"
                                },
                                {
                                    "domain": "auth.riotgames.com",
                                    "hostOnly": True,
                                    "httpOnly": False,
                                    "name": "sub",
                                    "path": "/",
                                    "persistent": True,
                                    "secureOnly": True,
                                    "value": self.cookie_values.sub
                                },
                                {
                                    "domain": "auth.riotgames.com",
                                    "hostOnly": True,
                                    "httpOnly": False,
                                    "name": "csid",
                                    "path": "/",
                                    "persistent": True,
                                    "secureOnly": True,
                                    "value": self.cookie_values.csid
                                }
                            ]
                        }
                    }
                }
            }
        }

        return yaml.dump(settings)

    def CreateGameModelWRegion(self):
        cookie_values = self.cookie_values
        settings = {
            "riot-login": {
                "persist": {
                    "region": "NA",
                    "session": {
                        "cookies": [
                            {
                                "domain": "riotgames.com",
                                "hostOnly": False,
                                "httpOnly": True,
                                "name": "tdid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": cookie_values.tdid
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "ssid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": cookie_values.ssid
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": True,
                                "name": "clid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": cookie_values.clid
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "sub",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": cookie_values.sub
                            },
                            {
                                "domain": "auth.riotgames.com",
                                "hostOnly": True,
                                "httpOnly": False,
                                "name": "csid",
                                "path": "/",
                                "persistent": True,
                                "secureOnly": True,
                                "value": cookie_values.csid
                            }
                        ]
                    }
                }
            }
        }

        return yaml.dump(settings)

    @staticmethod
    def CreateSettingsModel():
        settings = {
            "install": {
                "cohorts": {
                    "RC_15.new_lifecycle": "liveEnable9"
                },
                "lifecycle":  {
                    "enable_launch_on_computer_start_set_by_player": "false",
                    "enable_run_in_background_set_by_player": "false",
                },
                "mfa_notification_dismissed": "true",
                "globals": {
                    "region": "NA",
                    "locale": "en_US"
                },
                "multigame-client": {
                    "shortcut_created": "true"
                }
            }
        }

        return yaml.dump(settings)
