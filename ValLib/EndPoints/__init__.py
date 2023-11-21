from .Pvp import Pvp
from .Party import Party
from .CurrentGame import CurrentGame
from .Setting import Setting
from .Store import Store
from .PreGame import PreGame

from ..structs import Auth, ExtraAuth
from ..helper import get_region, get_shard, make_headers


class EndPoints:
    Pvp: Pvp
    Party: Party
    CurrentGame: CurrentGame
    Setting: Setting
    Store: Store
    PreGame: PreGame

    def __init__(self, auth: ExtraAuth, region=None, shard=None):
        self.auth = auth
        self.region = get_region(self.auth) if region is None else region
        self.shard = get_shard(self.region) if shard is None else shard

        self.Pvp = Pvp(self.auth, self.region, self.shard)
        self.Party = Party(self.auth, self.region, self.shard)
        self.CurrentGame = CurrentGame(self.auth, self.region, self.shard)
        self.Setting = Setting(self.auth, self.region, self.shard)
        self.Store = Store(self.auth, self.region, self.shard)
        self.PreGame = PreGame(self.auth, self.region, self.shard)


__all__ = {
    "EndPoints"
}
