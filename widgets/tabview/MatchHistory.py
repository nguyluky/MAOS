import asyncio
import json
import tkinter
import logging

from customtkinter import *

from Constant import Constant
from ValLib import EndPoints

from widgets.ImageHandel import async_load_img_from_url
from widgets.Structs import TabViewFrame


MAP_URL_2_NAME = {
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/Bonsai/Bonsai": "Split",
    "/Game/Maps/Canyon/Canyon": "Fracture",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/HURM/HURM_Alley/HURM_Alley": "District",
    "/Game/Maps/HURM/HURM_Bowl/HURM_Bowl": "Kasbah",
    "/Game/Maps/HURM/HURM_Yard/HURM_Yard": "Piazza",
    "/Game/Maps/Jam/Jam": "Lotus",
    "/Game/Maps/Juliett/Juliett": "Sunset",
    "/Game/Maps/Pitt/Pitt": "Pearl",
    "/Game/Maps/Port/Port": "Icebox",
    "/Game/Maps/Poveglia/Range": "The Range",
    "/Game/Maps/Triad/Triad": "Haven"
}

logger = logging.getLogger("main_app")


class Match(CTkFrame):
    def __init__(self, master, map, kda, score, type, won, agent, *args, **kwargs):
        super().__init__(master, height=60, border_color="#696969",
                         border_width=1, *args, **kwargs)

        # setup value
        self.loop = asyncio.get_event_loop()
        self.agent_url = agent
        # a = CTkImage(load_img_from_url('https://media.valorant-api.com/agents/e370fa57-4757-3604-3648-499e1f642d3f/displayicon.png'), size=(40,40))
        self.agent = CTkLabel(self, text='', height=40, width=40)
        self.agent.pack(side=LEFT, padx=10, pady=10)

        # map and type queue
        self.frame_type_map_name = CTkFrame(
            self, fg_color="transparent", width=100)

        # -- queue type --
        self.type = CTkLabel(self.frame_type_map_name, text=type,
                             width=100, anchor=SW, font=('Consolas', 17, "bold"))
        self.type.pack(side=TOP, expand=True, fill=BOTH, anchor=SW)
        # -- map name --
        self.map = CTkLabel(self.frame_type_map_name, text=map,
                            width=100, anchor=NW, font=('Consolas', 12, "normal"))
        self.map.pack(side=TOP, expand=True, fill=BOTH, anchor=NW)

        self.frame_type_map_name.pack(side=LEFT)

        # score
        self.team1 = CTkLabel(
            self, text=score[0], width=25, font=('Consolas', 12, "normal"))
        self.team1.pack(side=LEFT)

        self._ = CTkLabel(self, text=':', font=('Consolas', 12, "normal"))
        self._ .pack(side=LEFT)

        self.team2 = CTkLabel(
            self, text=score[1], width=25, font=('Consolas', 12, "normal"))
        self.team2.pack(side=LEFT)

        # kda frame
        self.kda_frame = CTkFrame(self, fg_color="transparent")
        self.kda_frame.pack(side=LEFT, padx=10)

        self.top = CTkLabel(self.kda_frame, text="K/D/A",
                            width=90, anchor=SE, font=('Consolas', 12, "normal"))
        self.top.pack(side=TOP, expand=True, fill=BOTH, anchor=SE)

        self.bott = CTkLabel(
            self.kda_frame, text=f"{kda[0]}/{kda[1]}/{kda[2]}", width=90, anchor=NE, font=('Consolas', 12, "normal"))
        self.bott.pack(side=TOP, expand=True, fill=BOTH, anchor=NE)

        # load agent image
        self.loop.create_task(self.get_agent_icon())

    async def get_agent_icon(self):
        img = await async_load_img_from_url(f'https://media.valorant-api.com/agents/{self.agent_url}/displayicon.png')
        ctkimg = CTkImage(img, size=(40, 40))
        self.agent.configure(image=ctkimg)


class MatchHistory(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # setup value
        self.is_endpoint_changed = False
        self.loop = asyncio.get_event_loop()
        self.height = 0
        self.width = 0
        self.frame_historys = []

        # render layout
        self.main_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)
        self.main_frame.columnconfigure(0, weight=1)

        a = Match(self.main_frame, "Ascent", (0, 0, 0), (0, 0),
                  'unrank', False, 'e370fa57-4757-3604-3648-499e1f642d3f')
        a.grid(row=0, column=0)

        self.queue_id = tkinter.StringVar(self,'All')
        self.match_type = CTkOptionMenu(self, width=60,
                                        values=[
                                            "All",
                                            "Competitive",
                                            "Premier",
                                            "Unrated",
                                            "Team Deathmatch",
                                            "Deathmatch",
                                            "Spike Rush",
                                            "Swiftplay",
                                            "Escalation",
                                            "Replication",
                                            "Snowball Fight"
                                        ],
                                        command=self.handel_option, variable=self.queue_id)

        Constant.Current_Acc.add_callback(self.current_change)
        self.bind('<Configure>', self.update_pos)

    def current_change(self, mod, value):
        self.is_endpoint_changed = True
        self.update_list()

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.match_type.place(y=10, x=self.width - 15, anchor=NE)

    def handel_option(self, value):
        self.update_list()

    def update_list(self):
        if not self.is_show:
            return
        
        value = self.queue_id.get()
        value = str(value).lower()
        if value == "all":
            value = None
        self.loop.create_task(self.get_match_history(value))
        self.is_endpoint_changed = False

    async def get_match_history(self, queue):
        logger.debug('get match history')
        endpoints: EndPoints = Constant.Current_Acc.get()
        data = await endpoints.Pvp.async_Match_History(None, 0, 20, queue)

        tasks = [self.loop.create_task(get_match_data(
            endpoints, i.match_id)) for i in data.history]

        data_r = await asyncio.gather(*tasks)
        # logger.debug(f'match data {data_r}')
        self.clear_()

        self.frame_historys = [
            Match(self.main_frame, map_, kda, score, queue, won, agent) for won, score, queue, agent, map_, kda in data_r
        ]
        self.render_()

    def clear_(self):
        for i in self.frame_historys:
            i.destroy()
        
        self.frame_historys.clear()

    def render_(self):
        
        for index, value in enumerate(self.frame_historys):
            value: Match
            value.grid(row=index, column=0, pady=5)

    def show(self):
        super().show()
        if self.is_endpoint_changed:
            self.update_list()
        
        


async def get_match_data(endpoints: EndPoints, math_id):
    match_det = await endpoints.Pvp.async_Match_Details(math_id)

    queue_id = match_det['matchInfo']['queueID']
    map_url = match_det['matchInfo']['mapId']
    map_url = MAP_URL_2_NAME[map_url]

    curr_acc: EndPoints = Constant.Current_Acc.get()
    playes: dict = match_det['players']

    team_id = None
    characterId = None
    kda = [0, 0, 0]
    for i in playes:
        if i['subject'] == curr_acc.auth.user_id:
            # get team id
            team_id = i['teamId']
            # get
            characterId = i["characterId"]

            # get kda
            kda[0] = i['stats']['kills']
            kda[1] = i['stats']['deaths']
            kda[2] = i['stats']['assists']

    if team_id is None:
        return

    # get your score
    teams: dict = match_det['teams']
    score = [0, 0]
    won: bool = None
    for i in teams:
        if i["teamId"] == team_id:
            score[0] = i['numPoints']
            won = i["won"]

    if queue_id == "deathmatch":
        score[1] = 40

    else:
        for i in teams:
            if i["won"] == (not won):
                score[1] = i['numPoints']

    return won, score, queue_id, characterId, map_url, kda
