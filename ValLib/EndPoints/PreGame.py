from uuid import UUID

import httpx

from ..structs import Auth, ExtraAuth
from ..helper import get_region, get_shard, make_headers


# ! not User
class PreGame:
    def __init__(self, auth: ExtraAuth, region=None, shard=None):
        self.auth = auth
        self.region = get_region(self.auth) if region is None else region
        self.shard = get_shard(self.region) if shard is None else shard

    def PreGame_Player(self, player_UUID=None):
        puuid = player_UUID if player_UUID is not None else self.auth.user_id

        url = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net/pregame/v1/players/{puuid}"

        headers = make_headers(self.auth)

        resp = httpx.get(url, headers=headers)

        return resp.json()
