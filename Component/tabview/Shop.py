import asyncio
import logging

import httpx

from Helper.Constant import Constant
from ValLib import EndPoints
from Component.Structs import TabViewFrame
from Component.tabview.ImageLabel import *

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
        self.bundle_label.grid(row=0, column=0, rowspan=4,
                               sticky=NSEW, padx=5, pady=5)
        self.bundle_label_prices = CTkLabel(self, text="0000", font=(
            "Consolas", 14), corner_radius=10, height=30)
        self.bundle_label_prices.grid(
            row=0, column=0, rowspan=4, sticky=SE, padx=15, pady=15)

        self.skins = [
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0)
        ]

        vp_icon = CTkImage(load_img(r'assets\img\vp.png'), size=(17, 17))
        
        self.prices = [
            CTkLabel(self, text="0000", font=("Consolas", 14), image=vp_icon, compound=LEFT, anchor=W),
            CTkLabel(self, text="0000", font=("Consolas", 14), image=vp_icon, compound=LEFT, anchor=W),
            CTkLabel(self, text="0000", font=("Consolas", 14), image=vp_icon, compound=LEFT, anchor=W),
            CTkLabel(self, text="0000", font=("Consolas", 14), image=vp_icon, compound=LEFT, anchor=W),
        ]

        # show skins
        for index, ele in enumerate(self.skins):
            ele.grid(row=index, column=1, sticky=NSEW, padx=5, pady=5)

        # show prices
        for index, ele in enumerate(self.prices):
            ele.grid(row=index, column=1, sticky=SE)
        Constant.Current_Acc.add_callback(self.handel_event)

    async def get_skin(self, uuid, index):
        ele = self.skins[index]
        skin_url = await get_weapon_skin_level_by_uuid(uuid)
        ele.set_img(url=skin_url)

    def set_prices(self, price, index):
        ele = self.prices[index]
        ele.configure(text=price)

    async def get_shop(self, endpoint: EndPoints):
        if not self.is_show:
            return

        logger.debug(f'get shope account {endpoint.auth.username}')
        data = await endpoint.Store.Storefront()
        bundle = data['FeaturedBundle']['Bundles'][0]['DataAssetID']
        skins = data["SkinsPanelLayout"]["SingleItemOffers"]

        bundle_url = await get_bundle_by_uuid(bundle)
        self.bundle_label.set_img(url=bundle_url)
        bundle_price = data['FeaturedBundle']['Bundles'][0]['TotalDiscountedCost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
        self.bundle_label_prices.configure(text=bundle_price)

        tasks = [self.loop.create_task(self.get_skin(id, index))
                 for index, id in enumerate(skins)]

        for i in data['SkinsPanelLayout']['SingleItemStoreOffers']:
            index = skins.index(i['OfferID'])

            price: dict = i['Cost']
            p = list(price.values())

            self.set_prices(p[0], index)

        self.is_endpoint_changed = False

    def show(self):
        super().show()
        endpont = Constant.Current_Acc.get()
        if isinstance(endpont, EndPoints) and self.is_endpoint_changed:
            self.loop.create_task(self.get_shop(endpont))
            self.last = endpont

    async def handel_event(self, mode, value):
        self.is_endpoint_changed = True
        await self.get_shop(value)
