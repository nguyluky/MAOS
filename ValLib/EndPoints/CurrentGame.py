from uuid import UUID

import httpx

from ..structs import Auth, ExtraAuth
from ..helper import get_region, get_shard, make_headers


class CurrentGame:
    def __init__(self, auth: ExtraAuth, region=None, shard=None):
        self.auth = auth
        self.region = get_region(self.auth) if region is None else region
        self.shard = get_shard(self.region) if shard is None else shard

    def Current_Game(self, player_UUID: UUID = None):
        puuid = player_UUID if player_UUID is not None else self.auth.user_id

        url = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net/core-game/v1/players/{puuid}"

        headers = make_headers(self.auth)

        resp = httpx.get(url, headers=headers)

        return resp.json()

    async def async_Current_Game(self, player_UUID: UUID = None) -> dict:
        puuid = player_UUID if player_UUID is not None else self.auth.user_id

        url = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net/core-game/v1/players/{puuid}"

        headers = make_headers(self.auth)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)

            return resp.json()

    async def async_Current_Game_Match(self, match_id: UUID = None) -> dict:
        url = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}"

        headers = make_headers(self.auth)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)

            return resp.json()


    def Current_Game_Match(self, match_id: UUID = None):
        url = f"https://glz-{self.region}-1.{self.shard}.a.pvp.net/core-game/v1/matches/{match_id}"

        headers = make_headers(self.auth)

        resp = httpx.get(url, headers=headers)

        return resp.json()
