from widgets.Variable import ListVariable, CustomVariable, Setting
from ValLib import ExtraAuth


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Constant(metaclass=SingletonMeta):
    Accounts: ListVariable[ExtraAuth] = ListVariable()
    EndPoints: ListVariable[EndPoints] = ListVariable()
    Current_Acc: CustomVariable = CustomVariable(None)  # return Endpoint
    Setting_Valorant: dict = {}
    Current_Acc_Setting: dict = {}
    App_Setting: Setting = None
    Is_Game_Run: bool = False
    Language: dict[str, str] = {}