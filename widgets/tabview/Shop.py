import asyncio
import logging

import httpx

from Constant import Constant
from ValLib import EndPoints
from widgets.Structs import TabViewFrame
from widgets.tabview.ImageLabel import *

logger = logging.getLogger("main_app")

async def get_weapon_skin_level_by_uuid(uuid): 
    logger.info('get skin id {}'.format(uuid))
    #  return url image skin
    url = f'https://valorant-api.com/v1/weapons/skinlevels/{uuid}'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

        data = resp.json()

        return data['data']['displayIcon']


async def get_bundle_by_uuid(uuid):
    logger.debug(f'get bundle id {uuid}')
    url = f"https://valorant-api.com/v1/bundles/{uuid}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        return data["data"]["displayIcon"]



class Shop(TabViewFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)
        self.is_endpoint_changed = False
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
        if not self.is_show:
            return
        
        logger.debug(f'get shope')
        data = await endpoint.Store.Storefront()
        bundle = data["FeaturedBundle"]["Bundle"]["DataAssetID"]
        skins = data["SkinsPanelLayout"]["SingleItemOffers"]

        bundle_url = await get_bundle_by_uuid(bundle)
        self.bundle_label.set_img(url=bundle_url)

        async def get_skin(uuid, index):
            ele = self.skins[index]
            skin_url = await get_weapon_skin_level_by_uuid(uuid)
            ele.set_img(url=skin_url)

        tasks = [self.loop.create_task(get_skin(id, index)) for index, id in enumerate(skins)]
        self.is_endpoint_changed = False

    def set_(self, data):
        pass

    def show(self):
        super().show()
        endpont = Constant.Current_Acc.get()
        if isinstance(endpont, EndPoints) and self.is_endpoint_changed:
            self.loop.create_task(self.get_shop(endpont))
            self.last = endpont

    async def handel_event(self, mode, value):
        self.is_endpoint_changed = True
        await self.get_shop(value)
