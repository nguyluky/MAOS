import asyncio

from customtkinter import *

from ValLib import EndPoints
from widgets.Structs import TabViewFrame
from Constant import Constant

class Match(CTkFrame):
    def __init__(self, master, map, rank, kda, sor ,*args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        
        


class MatchHistory(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # setup value
        self.loop = asyncio.get_event_loop()
        self.height = 0
        self.width = 0
        self.match_history = {

        }

        # render layout
        self.main_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.place(x=0, y=0, relheight=1, relwidth=1)
        
        self.match_type = CTkOptionMenu(self, width=60,
                                        values=[
                                                "Standard",
                                                "Deathmatch",
                                                "Escalation",
                                                "Team Deathmatch",
                                                "Onboarding",
                                                "Replication",
                                                "Spike Rush",
                                                "PRACTICE",
                                                "Snowball Fight",
                                                "Swiftplay",
                                            ],
                                        command=self.handel_option)
        
        Constant.Current_Acc.add_callback(self.current_change)
        self.loop.create_task(self.get_match_history())
        self.bind('<Configure>', self.update_pos)
        
    def current_change(self, mod, value):
        pass
    

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.match_type.place(y=10 , x = self.width - 15, anchor=NE)

    def handel_option(self, value):
        print(value)

    async def get_match_history(self):
        endpoints: EndPoints = Constant.Current_Acc.get()
        data = await endpoints.Pvp.async_Match_History()
        for i in data.history:
            print(i.queue_id)

    def show(self):
        super().show()
