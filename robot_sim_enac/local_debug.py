from robot_sim_enac.data_types import data_type, PositionOrientedTimed
from robot_sim_enac.interface import Interface
import asyncio
import sched
from time import time, sleep

class LocalDebug(Interface):
    """
    Allows display only - no interraction with the sim !
    """
    def __init__(self, robot_name):
        super().__init__(robot_name)
        self.tasks = []
        self.schedulder =sched.scheduler(time, sleep)


    def start(self, *args):
        print("local debug started !")

    def process_com(self):
        self.schedulder.run(False)
        pass

    async def publish_regularly(self, get_data_callback_str, timer):
        while(True):
            print(get_data_callback_str())
            await asyncio.sleep(timer)

    def stop(self):
        print("TODO : stop the local_debug")
        #TODO : implement something
        pass


    def update_data_continuous(self, name : str, dataType: data_type, get_data_callback, rate : float):
        if type(get_data_callback()) == PositionOrientedTimed:
            g = get_data_callback()
            print(g.x, g.y, g.theta, g.vx, g.vz, g.stamp)
        else:
            print(get_data_callback())
        self.schedulder.enter(rate, 3, self.update_data_continuous, (name, dataType, get_data_callback, rate))

    def register_msg_callback(self, name: str, dataType:data_type, set_data_callback):
        print("warning, register_msg_callback not supported with local_debug")
        pass