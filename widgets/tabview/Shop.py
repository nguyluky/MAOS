import asyncio

import httpx

from Constant import Constant
from ValLib import EndPoints
from widgets.Structs import TabViewFrame
from widgets.tabview.ImageLabel import *


async def get_weapon_skin_level_by_uuid(uuid):
    #  return url image skin
    url = f'https://valorant-api.com/v1/weapons/skinlevels/{uuid}'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

        data = resp.json()

        return data['data']['displayIcon']


async def get_bundle_by_uuid(uuid):
    url = f"https://valorant-api.com/v1/bundles/{uuid}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        return data["data"]["displayIcon"]



class Shop(TabViewFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        # init value
        self.loop = asyncio.get_event_loop()

        # setup layout
        self.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.grid_columnconfigure(0, weight=3, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')

        self.bundle_label = ImageLabel(self)
        self.bundle_label.grid(row=0, column=0, rowspan=4, sticky=NSEW, padx=5, pady=5)

        self.skins = [
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0)
        ]
        for index, ele in enumerate(self.skins):
            ele.grid(row=index, column=1, sticky=NSEW, padx=5, pady=5)

        Constant.Current_Acc.add_callback(self.handel_event)

    async def get_shop(self, endpoint: EndPoints):
        data = await endpoint.Store.Storefront()
        bundle = data["FeaturedBundle"]["Bundle"]["DataAssetID"]
        skins = data["SkinsPanelLayout"]["SingleItemOffers"]

        bundle_url = await get_bundle_by_uuid(bundle)
        if self.is_show:
            self.bundle_label.set_img(url=bundle_url)

        async def get_skin(uuid, index):
            ele = self.skins[index]
            skin_url = await get_weapon_skin_level_by_uuid(uuid)
            if self.is_show:
                ele.set_img(url=skin_url)

        tasks = [self.loop.create_task(get_skin(id, index)) for index, id in enumerate(skins)]

    def set_(self, data):
        pass

    def show(self):
        super().show()
        endpont = Constant.Current_Acc.get()
        if isinstance(endpont, EndPoints):
            self.loop.create_task(self.get_shop(Constant.Current_Acc.get()))

    async def handel_event(self, mode, value):
        await self.get_shop(value)
