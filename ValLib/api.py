import json
from typing import Any

import requests
from requests import Response
import httpx

from .parsing import *
from .helper import make_headers
from .structs import Auth, ExtraAuth


def get_api(url, auth: Auth) -> Any:
    r = requests.get(url, headers=make_headers(auth))
    jsonData = json.loads(r.text)

    return jsonData


def put_api(url, auth: Auth, data) -> Response:

    req = requests.put(url, headers=make_headers(auth), json=data)
    return req


def post_api(url, auth: Auth, data):

    req = requests.post(url, headers=make_headers(auth), json=data)
    return req


def get_preference(auth: Auth) -> Any:
    apiURL = "https://playerpreferences.riotgames.com/playerPref/v3/getPreference/Ares.PlayerSettings"
    jsonData = get_api(apiURL, auth)
    if "data" not in jsonData:
        return {}
    data = zloads(jsonData["data"])
    return data


def set_preference(auth: Auth, data) -> Response:
    rawData = {
        "type": "Ares.PlayerSettings",
        "data": zdumps(data)
    }
    apiURL = "https://playerpreferences.riotgames.com/playerPref/v3/savePreference"
    req = put_api(apiURL, auth, rawData)
    return req


def get_load_out(auth: ExtraAuth) -> Any:
    apiURL = f"https://pd.{auth.region}.a.pvp.net/personalization/v2/players/{auth.user_id}/playerloadout"
    data = get_api(apiURL, auth)
    del data['Subject']
    del data['Version']
    return data


def set_load_out(auth: ExtraAuth, data) -> Response:
    apiURL = f"https://pd.{auth.region}.a.pvp.net/personalization/v2/players/{auth.user_id}/playerloadout"
    data = put_api(apiURL, auth, data)
    return data


def get_session(loadAuth: ExtraAuth):
    region = loadAuth.region
    apiURL = f"https://glz-{region}-1.{region}.a.pvp.net/session/v1/sessions/{loadAuth.user_id}"
    return get_api(apiURL, loadAuth.auth)


def get_region(auth: Auth) -> str:
    data = {
        "id_token": auth.id_token
    }
    apiURL = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    data = put_api(apiURL, auth, data)
    jsonData = json.loads(data.text)
    region = jsonData["affinities"]["live"]
    return region


def get_shard(region: str) -> str:
    if region in ["latam", "br", "pbe"]:
        return "na"
    return region


# async fn
async def async_get_api(url, auth: Auth):
    log(Level.DEBUG, f"ASYNC GET {url}", "network")
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=make_headers(auth))
        return r.json()


async def async_put_api(url, auth: Auth, data) -> httpx.Response:
    log(Level.DEBUG, f"ASYNC PUT {url}", "network")
    async with httpx.AsyncClient() as client:
        r = await client.put(url, headers=make_headers(auth), json=data)
        return r


async def async_post_api(url, auth: Auth, data):
    log(Level.DEBUG, f"ASYNC POST {url}", "network")
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=make_headers(auth), json=data)
        return r


async def async_get_preference(auth: Auth) -> Any:
    pass


async def async_set_preference(auth: Auth, data) -> Response:
    pass


async def async_get_load_out(auth: ExtraAuth) -> Any:
    pass


async def async_set_load_out(auth: ExtraAuth, data) -> Response:
    pass


async def async_get_session(loadAuth: ExtraAuth):
    pass


async def async_get_region(auth: Auth) -> str:
    pass


async def async_get_shard(region: str) -> str:
    pass
