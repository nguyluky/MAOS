import httpx
import json
from uuid import UUID
from ..structs import Auth, ExtraAuth
from ..helper import make_headers, get_shard, get_region
from .structs import PlayerLoadout, PlayerMMRResponse, MatchHistoryResponse


class Store:
    def __init__(self, auth: ExtraAuth, region=None, shard=None):
        self.auth = auth
        self.region = get_region(self.auth) if region is None else region
        self.shard = get_shard(self.region) if shard is None else shard

    async def Storefront(self, player_UUID: UUID = None):
        puuid = player_UUID if player_UUID is not None else self.auth.user_id
        headers = make_headers(self.auth)
        url = f"https://pd.{self.shard}.a.pvp.net/store/v2/storefront/{puuid}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            return resp.json()

