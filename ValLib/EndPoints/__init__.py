from .Pvp import Pvp as Pvp_
from .Party import Party as Party_
from .CurrentGame import CurrentGame as CurrentGame_
from .Setting import Setting as Setting_
from .Store import Store as Store_
from .PreGame import PreGame as PreGame_

from ..structs import Auth, ExtraAuth
from ..helper import get_region, get_shard, make_headers


class EndPoints:
    Pvp: Pvp_
    Party: Party_
    CurrentGame: CurrentGame_
    Setting: Setting_
    Store: Store_
    PreGame: PreGame_

    def __init__(self, auth: ExtraAuth, region=None, shard=None):
        self.auth = auth
        self.region = get_region(self.auth) if region is None else region
        self.shard = get_shard(self.region) if shard is None else shard

        self.Pvp = Pvp_(self.auth, self.region, self.shard)
        self.Party = Party_(self.auth, self.region, self.shard)
        self.CurrentGame = CurrentGame_(self.auth, self.region, self.shard)
        self.Setting = Setting_(self.auth, self.region, self.shard)
        self.Store = Store_(self.auth, self.region, self.shard)
        self.PreGame = PreGame_(self.auth, self.region, self.shard)


__all__ = {
    "EndPoints"
}
